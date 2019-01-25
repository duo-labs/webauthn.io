package server

import (
	"encoding/json"
	"fmt"
	"html/template"
	"net/http"
)

// defaultTemplates are included every time a template is rendered.
var defaultTemplates = []string{"./templates/base.html", "./templates/info.html"}

// JSONResponse attempts to set the status code, c, and marshal the given
// interface, d, into a response that is written to the given ResponseWriter.
func jsonResponse(w http.ResponseWriter, d interface{}, c int) {
	dj, err := json.MarshalIndent(d, "", "  ")
	if err != nil {
		http.Error(w, "Error creating JSON response", http.StatusInternalServerError)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(c)
	fmt.Fprintf(w, "%s", dj)
}

// renderTemplate renders the template to the ResponseWriter
func renderTemplate(w http.ResponseWriter, f string, data interface{}) {
	t, err := template.ParseFiles(append(defaultTemplates, fmt.Sprintf("./templates/%s", f))...)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	t.ExecuteTemplate(w, "base", data)
}
