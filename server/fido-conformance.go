package server

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/duo-labs/webauthn/protocol"

	"github.com/duo-labs/webauthn.io/fido"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/gorilla/mux"
)

func (ws *Server) AddConformanceEndpoints(r *mux.Router) {
	r.HandleFunc("/fido/attestation/options", ws.HandleFIDOAttestationOptions).Methods("POST")
	r.HandleFunc("/fido/attestaion/result", ws.HandleFIDOAttestationResults).Methods("POST")
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

	fmt.Printf("got data: %+v\n", request)

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

	credentialOptions, data, err := ws.webauthn.BeginRegistration(user,
		webauthn.WithConveyancePreference(conveyancePref))
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = ws.store.SaveWebauthnSession("registration", data, r, w)
	if err != nil {
		jsonResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := fido.ConformanceResponse{
		credentialOptions.Response, "ok", "",
	}

	base64.URLEncoding.Encode(response.User.ID, credentialOptions.Response.User.ID)

	jsonResponse(w, response, http.StatusOK)
	return
}

func (ws *Server) HandleFIDOAttestationResults(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm
	if err != nil {
		jsonResponse(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

}

func (ws *Server) HandleFIDOAssertionOptions(w http.ResponseWriter, r *http.Request) {

}

func (ws *Server) HandleFIDOAssertionResults(w http.ResponseWriter, r *http.Request) {

}
