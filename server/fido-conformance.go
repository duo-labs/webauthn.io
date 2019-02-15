package server

import (
	"net/http"

	"github.com/duo-labs/webauthn.io/fido"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/gorilla/mux"
)

func (ws *Server) AddConformanceEndpoints(r *mux.Router) {
	r.HandleFunc("/fido/attestation/options", ws.HandleFIDOAttestationOptions).Methods("POST")
	r.HandleFunc("/fido/attestaion/result", ws.HandleFIDOAttestationResults).Methods("POST")
	r.HandleFunc("/fido/assertion/options", ws.HandleFIDOAssertionOptions).Methods("POST")
	r.HandleFunc("/fido/assertion/result", ws.HandleFIDOAssertionResults).Methods("POST")
}

func (ws *Server) HandleFIDOAttestationOptions(w http.ResponseWriter, r *http.Request) {
	// The fido conformance tool hands us JSON in post data
	parseErr := r.ParseForm
	if parseErr != nil {
		jsonResponse(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	request := fido.ConformanceRequest{
		DisplayName:     r.FormValue("displayName"),
		AttestationType: r.FormValue("attestation"),
		Username:        r.FormValue("username"),
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
