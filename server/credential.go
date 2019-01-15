package server

import (
	"net/http"
	"strings"

	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/duo-labs/webauthn/protocol"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/gorilla/mux"
)

// RequestNewCredential begins a Credential Registration Request, returning a
// PublicKeyCredentialCreationOptions object
func (ws *Server) RequestNewCredential(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	username := vars["name"]

	// Most times relying parties will choose these.
	attType := r.FormValue("attType")
	authType := r.FormValue("authType")

	// models.GetorCreateUser(User)
	user, err := models.GetUserByUsername(username)
	if err != nil {
		user = models.User{
			DisplayName: strings.Split(username, "@")[0],
			Username:    username,
		}
		err = models.PutUser(&user)
		if err != nil {
			jsonResponse(w, "Error creating new user", http.StatusInternalServerError)
			return
		}
	}

	credentialOptions, sessionData, err := ws.webauthn.BeginRegistration(user,
		webauthn.WithAuthenticatorSelection(
			protocol.AuthenticatorSelection{
				AuthenticatorAttachment: protocol.AuthenticatorAttachment(authType),
				RequireResidentKey:      false,
				UserVerification:        protocol.VerificationPreferred,
			}),
		webauthn.WithConveyancePreference(protocol.ConveyancePreference(
			attType)))
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Save the session data as marshaled JSON
	err = ws.store.SaveWebauthnSession("registration", sessionData, r, w)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Return the PublicKeyCreationOptions back to the browser
	jsonResponse(w, credentialOptions, http.StatusOK)
	return
}

// MakeNewCredential attempts to make a new credential given an authenticator's response
func (ws *Server) MakeNewCredential(w http.ResponseWriter, r *http.Request) {
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
	// Can perform additional checks
	// Finally, save the credential (and authenticator, if needed) to the
	// database
	authenticator, err := models.GetOrCreateAuthenticator(cred.Authenticator)
	if err != nil {
		log.Errorf("error creating authenticator: %v", err)
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	c := &models.Credential{
		Authenticator: authenticator,
		UserID:        user.ID,
		PublicKey:     cred.PublicKey,
		CredentialID:  cred.ID,
	}
	err = models.CreateCredential(c)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	jsonResponse(w, http.StatusText(http.StatusCreated), http.StatusCreated)
}

// GetCredentials gets a user's credentials from the db
func (ws *Server) GetCredentials(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	username := vars["name"]
	u, err := models.GetUserByUsername(username)
	if err != nil {
		log.Errorf("user not found: %s: %s", username, err)
		jsonResponse(w, "User not found", http.StatusNotFound)
		return
	}
	cs, err := models.GetCredentialsForUser(&u)
	if err != nil {
		log.Error(err)
		jsonResponse(w, "Credentials not found", http.StatusNotFound)
		return
	}
	jsonResponse(w, cs, http.StatusOK)
}

// DeleteCredential deletes a credential from the db
func (ws *Server) DeleteCredential(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	credID := vars["id"]
	err := models.DeleteCredentialByID(credID)
	log.Infof("deleting credential: %s", credID)
	if err != nil {
		log.Errorf("error deleting credential: %s", err)
		jsonResponse(w, "Credential not Found", http.StatusNotFound)
		return
	}
	jsonResponse(w, "Success", http.StatusOK)
}
