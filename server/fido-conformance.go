package server

import (
	"encoding/base64"
	"encoding/json"
	"net/http"

	"github.com/duo-labs/webauthn/protocol"
	"github.com/jinzhu/gorm"

	"github.com/duo-labs/webauthn.io/fido"
	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/gorilla/mux"
)

func (ws *Server) AddConformanceEndpoints(r *mux.Router) {
	r.HandleFunc("/fido/attestation/options", ws.HandleFIDOAttestationOptions).Methods("POST")
	r.HandleFunc("/fido/attestation/result", ws.HandleFIDOAttestationResults).Methods("POST")
	r.HandleFunc("/fido/assertion/options", ws.HandleFIDOAssertionOptions).Methods("POST")
	r.HandleFunc("/fido/assertion/result", ws.HandleFIDOAssertionResults).Methods("POST")
}

func (ws *Server) HandleFIDOAttestationOptions(w http.ResponseWriter, r *http.Request) {
	var request fido.ConformanceRequest
	decodeErr := json.NewDecoder(r.Body).Decode(&request)
	if decodeErr != nil {
		jsonResponse(w, decodeErr, http.StatusBadRequest)
		return
	}

	user, err := models.GetUserByUsername(request.Username)
	if err != nil {
		user = models.User{
			DisplayName: request.DisplayName,
			Username:    request.Username,
		}
		err = models.PutUser(&user)
		if err != nil {
			jsonResponse(w, "Error creating new user", http.StatusInternalServerError)
			return
		}
	}

	conveyancePref := protocol.ConveyancePreference(protocol.PreferNoAttestation)
	if request.AttestationType != "" {
		conveyancePref = protocol.ConveyancePreference(request.AttestationType)
	}

	credentials := user.WebAuthnCredentials()
	excludedCredentials := make([]protocol.CredentialDescriptor, len(credentials))

	for i, credential := range credentials {
		var credentialDescriptor protocol.CredentialDescriptor
		credentialDescriptor.CredentialID = credential.ID
		credentialDescriptor.Type = protocol.PublicKeyCredentialType
		excludedCredentials[i] = credentialDescriptor
	}
	credentialOptions, data, err := ws.webauthn.BeginRegistration(user,
		webauthn.WithConveyancePreference(conveyancePref),
		webauthn.WithAuthenticatorSelection(
			protocol.AuthenticatorSelection{
				AuthenticatorAttachment: request.AuthenticatorSelection.AuthenticatorAttachment,
				RequireResidentKey:      request.AuthenticatorSelection.RequireResidentKey,
				UserVerification:        request.AuthenticatorSelection.UserVerification,
			}),
		webauthn.WithExtensions(request.Extensions),
		webauthn.WithExclusions(excludedCredentials),
	)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := fido.MarshallTestCreationResponse(credentialOptions.Response)

	//fmt.Printf("challenge is : %s\n", response.Challenge)

	data.Challenge = response.Challenge
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = ws.store.SaveWebauthnSession("registration", data, r, w)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	jsonResponse(w, response, http.StatusOK)
	return
}

func (ws *Server) HandleFIDOAttestationResults(w http.ResponseWriter, r *http.Request) {
	errForm := r.ParseForm()
	if errForm != nil {
		jsonResponse(w, "Error parsing form data", http.StatusBadRequest)
		return
	}
	//fmt.Printf("During results, got req: %+v\n", r)
	// Load the session data
	sessionData, err := ws.store.GetWebauthnSession("registration", r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusBadRequest)
		return
	}
	// Get the user associated with the credential
	user, err := models.GetUser(models.BytesToID(sessionData.UserID))
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// Verify that the challenge succeeded
	cred, err := ws.webauthn.FinishRegistration(user, sessionData, r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// If needed, you can perform additional checks here to ensure the
	// authenticator and generated credential conform to your requirements.

	// Finally, save the credential and authenticator to the
	// database
	authenticator, err := models.CreateAuthenticator(cred.Authenticator)
	if err != nil {
		log.Errorf("error creating authenticator: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// For our use case, we're encoding the raw credential ID as URL-safe
	// base64 since we anticipate rendering it in templates. If you choose to
	// do this, make sure to decode the credential ID before passing it back to
	// the webauthn library.
	credentialID := base64.RawURLEncoding.EncodeToString(cred.ID)
	c := &models.Credential{
		Authenticator:   authenticator,
		AuthenticatorID: authenticator.ID,
		UserID:          user.ID,
		PublicKey:       cred.PublicKey,
		CredentialID:    credentialID,
	}
	err = models.CreateCredential(c)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	result := &protocol.ServerResponse{
		Status:  protocol.StatusOk,
		Message: "",
	}
	jsonResponse(w, result, http.StatusCreated)
	return
}

func (ws *Server) HandleFIDOAssertionOptions(w http.ResponseWriter, r *http.Request) {
	var request fido.ConformanceRequest
	decodeErr := json.NewDecoder(r.Body).Decode(&request)
	if decodeErr != nil {
		jsonResponse(w, decodeErr, http.StatusBadRequest)
		return
	}
	if request.Username == "" {
		jsonResponse(w, "No username specified", http.StatusBadRequest)
		return
	}

	user, err := models.GetUserByUsername(request.Username)
	if err == gorm.ErrRecordNotFound {
		log.Errorf("error creating assertion: user doesn't exist: %s", request.Username)
		jsonResponse(w, "User doesn't exist", http.StatusBadRequest)
		return
	}

	assertion, sessionData, err := ws.webauthn.BeginLogin(user, webauthn.WithUserVerification(request.UserVerification))
	if err != nil {
		log.Errorf("error creating assertion: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = ws.store.SaveWebauthnSession("assertion", sessionData, r, w)
	if err != nil {
		log.Errorf("error creating assertion session: error marshaling session: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response := fido.MarshallTestRequestResponse(*assertion)
	response.Extensions = request.Extensions
	response.UserVerification = request.UserVerification
	jsonResponse(w, response, http.StatusOK)
}

func (ws *Server) HandleFIDOAssertionResults(w http.ResponseWriter, r *http.Request) {
	errForm := r.ParseForm()
	if errForm != nil {
		jsonResponse(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	sessionData, err := ws.store.GetWebauthnSession("assertion", r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusBadRequest)
		return
	}
	// Get the user associated with the credential
	user, err := models.GetUser(models.BytesToID(sessionData.UserID))
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	log.Infof("Finishing authentication with user: %s\n", user.Username)
	// With the session data retrieved, we need to call webauthn.FinishLogin to
	// verify the signed challenge. This returns the webauthn.Credential that
	// was used to authenticate.
	cred, err := ws.webauthn.FinishLogin(user, sessionData, r)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// At this point, we've confirmed the correct authenticator has been
	// provided and it passed the challenge we gave it. We now need to make
	// sure that the sign counter is higher than what we have stored to help
	// give assurance that this credential wasn't cloned.
	if cred.Authenticator.CloneWarning {
		log.Errorf("credential appears to be cloned: %s", err)
		jsonResponse(w, ErrCredentialCloned, http.StatusForbidden)
		return
	}
	// We're logged in! All that's left is to update the sign count with the
	// new value we received. We could join the tables on the CredentialID
	// field, but for our purposes we'll just get the stored credential and
	// use that to find the authenticator we need to update.
	credentialID := base64.RawURLEncoding.EncodeToString(cred.ID)
	storedCredential, err := models.GetCredentialForUser(&user, credentialID)
	if err != nil {
		log.Errorf("error getting credentials for user: %s", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	err = models.UpdateAuthenticatorSignCount(storedCredential.AuthenticatorID, cred.Authenticator.SignCount)
	if err != nil {
		log.Errorf("error updating sign count: %s", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	err = ws.store.Set("user_id", user.ID, r, w)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	result := &protocol.ServerResponse{
		Status:  protocol.StatusOk,
		Message: "",
	}
	jsonResponse(w, result, http.StatusOK)

}
