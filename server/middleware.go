package server

import (
	"context"
	"net/http"

	"github.com/duo-labs/webauthn.io/models"
)

// LoginRequired sets a context variable with the user loaded from the user ID
// stored in the session cookie
func (ws *Server) LoginRequired(next http.HandlerFunc) http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		session, _ := ws.store.Get(r, "webauthn_io")
		// Load the user from the database and store it in the request context
		if id, ok := session.Values["user_id"]; ok {
			u, err := models.GetUser(id.(uint))
			if err != nil {
				r = r.WithContext(context.WithValue(r.Context(), "user", nil))
			} else {
				r = r.WithContext(context.WithValue(r.Context(), "user", u))
			}
		} else {
			r = r.WithContext(context.WithValue(r.Context(), "user", nil))
		}

		// If we have a valid user, allow access to the handler. Otherwise,
		// redirect to the main login page.
		if u := r.Context().Value("user"); u != nil {
			next.ServeHTTP(w, r)
		} else {
			http.Redirect(w, r, "/", http.StatusTemporaryRedirect)
		}
	})
}
