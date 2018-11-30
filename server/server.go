package server

import (
	"context"
	"net"
	"net/http"
	"time"

	"log"

	"github.com/duo-labs/webauthn.io/config"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
)

var store = sessions.NewCookieStore([]byte("duo-rox"))

// Timeout is the number of seconds to attempt a graceful shutdown, or
// for timing out read/write operations
const Timeout = 5 * time.Second

// Server is a configurable HTTP server that implements a demo of the WebAuthn
// specification
type Server struct {
	server *http.Server
	config *config.Config
}

// NewServer returns a new instance of a Server configured with the provided
// configuration
func NewServer(config *config.Config) *Server {
	addr := net.JoinHostPort(config.HostAddress, config.HostPort)
	if config.HasProxy {
		addr = config.HostPort
	}
	defaultServer := &http.Server{
		Addr:         addr,
		ReadTimeout:  Timeout,
		WriteTimeout: Timeout,
	}
	ws := &Server{
		server: defaultServer,
		config: config,
	}
	ws.registerRoutes()
	return ws
}

// Start starts the underlying HTTP server
func (ws *Server) Start() error {
	log.Printf("Starting webauthn server at %s", ws.server.Addr)
	return ws.server.ListenAndServe()
}

// Shutdown attempts to gracefully shutdown the underlying HTTP server.
func (ws *Server) Shutdown() error {
	ctx, cancel := context.WithTimeout(context.Background(), Timeout)
	defer cancel()
	return ws.server.Shutdown(ctx)
}

func (ws *Server) registerRoutes() {
	router := mux.NewRouter()
	// New handlers should be added here
	router.HandleFunc("/", ws.Login)
	router.HandleFunc("/dashboard/{name}", ws.Index)
	router.HandleFunc("/dashboard", ws.Index)
	router.HandleFunc("/makeCredential/{name}", ws.RequestNewCredential).Methods("GET")
	router.HandleFunc("/makeCredential", ws.MakeNewCredential).Methods("POST")
	router.HandleFunc("/assertion/{name}", ws.GetAssertion).Methods("GET")
	router.HandleFunc("/assertion", ws.MakeAssertion).Methods("POST")
	router.HandleFunc("/user", ws.CreateNewUser).Methods("POST")
	router.HandleFunc("/user/{name}", ws.GetUser).Methods("GET")
	router.HandleFunc("/credential/{name}", ws.GetCredentials).Methods("GET")
	router.HandleFunc("/credential/{id}", ws.DeleteCredential).Methods("DELETE")
	router.PathPrefix("/").Handler(http.FileServer(http.Dir("./static/")))
	ws.server.Handler = router
}
