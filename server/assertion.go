package server

import (
	"encoding/base64"
	"errors"
	"net/http"

	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/gorilla/mux"
	"github.com/jinzhu/gorm"
)

// ErrCredentialCloned occurs when an authenticator provides a sign count
// during assertion that is lower than the previously recorded sign count, as
// this would indicate that the authenticator may have been cloned.
var ErrCredentialCloned = errors.New("credential appears to have been cloned")

// GetAssertion - assemble the data we need to make an assertion against
// a given user and authenticator
func (ws *Server) GetAssertion(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	username := vars["name"]
	// TODO: Change these to POST's
	//username := r.FormValue("username")
	if username == "" {
		jsonResponse(w, "No username specified", http.StatusBadRequest)
		return
	}

	user, err := models.GetUserByUsername(username)
	if err == gorm.ErrRecordNotFound {
		log.Errorf("error creating assertion: user doesn't exist: %s", username)
		jsonResponse(w, "User doesn't exist", http.StatusBadRequest)
		return
	}

	assertion, sessionData, err := ws.webauthn.BeginLogin(user)
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

	jsonResponse(w, assertion, http.StatusOK)
}

// MakeAssertion validates the assertion data provided by the authenticator and
// responds whether or not it was successful alongside the relevant credential.
func (ws *Server) MakeAssertion(w http.ResponseWriter, r *http.Request) {
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
	jsonResponse(w, user, http.StatusOK)
}
