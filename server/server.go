package server

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"time"

	"log"

	"github.com/duo-labs/webauthn.io/config"
	"github.com/duo-labs/webauthn.io/session"
	"github.com/duo-labs/webauthn/metadata"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/gorilla/mux"
	uuid "github.com/satori/go.uuid"
)

// Timeout is the number of seconds to attempt a graceful shutdown, or
// for timing out read/write operations
const Timeout = 5 * time.Second

// Option is an option that sets a particular value for the server
type Option func(*Server)

// Server is a configurable HTTP server that implements a demo of the WebAuthn
// specification
type Server struct {
	server   *http.Server
	config   *config.Config
	webauthn *webauthn.WebAuthn
	store    *session.Store
}

// NewServer returns a new instance of a Server configured with the provided
// configuration
func NewServer(config *config.Config, opts ...Option) (*Server, error) {
	addr := net.JoinHostPort(config.HostAddress, config.HostPort)
	defaultServer := &http.Server{
		Addr:         addr,
		ReadTimeout:  Timeout,
		WriteTimeout: Timeout,
	}
	defaultStore, err := session.NewStore()
	if err != nil {
		return nil, err
	}
	defaultWebAuthn, _ := webauthn.New(&webauthn.Config{
		RPDisplayName: config.RelyingParty,
		RPID:          config.RelyingParty,
	})
	ws := &Server{
		config:   config,
		server:   defaultServer,
		store:    defaultStore,
		webauthn: defaultWebAuthn,
	}
	for _, opt := range opts {
		opt(ws)
	}
	ws.registerRoutes()
	return ws, nil
}

// WithWebAuthn sets the webauthn configuration for the server
func WithWebAuthn(w *webauthn.WebAuthn) Option {
	return func(ws *Server) {
		ws.webauthn = w
	}
}

// Start starts the underlying HTTP server
func (ws *Server) Start() error {
	log.Printf("Starting webauthn server at %s", ws.server.Addr)
	return ws.server.ListenAndServeTLS("server.crt", "server.key")
}

// Shutdown attempts to gracefully shutdown the underlying HTTP server.
func (ws *Server) Shutdown() error {
	ctx, cancel := context.WithTimeout(context.Background(), Timeout)
	defer cancel()
	return ws.server.Shutdown(ctx)
}

func (ws *Server) registerRoutes() {
	router := mux.NewRouter()
	// Unauthenticated handlers for registering a new credential and logging in.
	router.HandleFunc("/", ws.Login)
	router.HandleFunc("/makeCredential/{name}", ws.RequestNewCredential).Methods("GET")
	router.HandleFunc("/makeCredential", ws.MakeNewCredential).Methods("POST")
	router.HandleFunc("/assertion/{name}", ws.GetAssertion).Methods("GET")
	router.HandleFunc("/assertion", ws.MakeAssertion).Methods("POST")
	router.HandleFunc("/user/{name}/exists", ws.UserExists).Methods("GET")

	// Authenticated handlers for viewing credentials after logging in
	router.HandleFunc("/dashboard", ws.LoginRequired(ws.Index))

	if ws.config.ExposeFIDO {
		fmt.Println("Exposing FIDO Conformance Endpoints")
		ws.AddConformanceEndpoints(router)
		client := NewClient(nil)
		client.GetConformanceMetadata("https://" + ws.config.RelyingParty + ":" + ws.config.HostPort + "/fido")
		fmt.Println("Finished loading FIDO Conformance Metadata")
	} else {
		mdskey := os.Getenv("FIDO2_MDSAccessKey")
		if len(mdskey) != 0 {
			client := NewClient(nil)
			client.GetMetadata("/?token=" + mdskey)
		}
	}

	// Static file serving
	router.PathPrefix("/").Handler(http.FileServer(http.Dir("./static/")))
	ws.server.Handler = router
}

type Client struct {
	httpClient *http.Client
}

func NewClient(httpClient *http.Client) *Client {
	if httpClient == nil {
		httpClient = &http.Client{
			Timeout: time.Second * 30,
		}
	}
	return &Client{httpClient: httpClient}
}

func (c *Client) GetMetadata(e string) {
	toc, alg, err := metadata.ProcessMDSTOC("https://mds2.fidoalliance.org", e, *c.httpClient)
	if err != nil {
		fmt.Println(err)
		return
	}
	for _, entry := range toc.Entries {
		if entry.AaGUID == "" {
			continue
		}
		ms, err := metadata.GetMetadataStatement(entry, e, alg, *c.httpClient)
		if err != nil {
			fmt.Println(err)
		} else {
			aaguid, err := uuid.FromString(ms.AaGUID)
			if err != nil {
				fmt.Println(err)
			} else {
				entry.MetadataStatement = ms
				metadata.Metadata[aaguid] = entry
				fmt.Println("Loaded metadata for " + entry.MetadataStatement.Description + ", AAGUID: " + entry.MetadataStatement.AaGUID)
			}
		}
	}
	LoadMetadataFromFolder("CustomMetadata")
}

func LoadMetadataFromFolder(folder string) {
	files, err := ioutil.ReadDir(folder)
	if err != nil {
		fmt.Println(err)
		return
	}
	reports := []metadata.StatusReport{metadata.StatusReport{
		Status: metadata.NotFidoCertified,
	}}

	for _, file := range files {
		b, err := ioutil.ReadFile(folder + "/" + file.Name())
		if err != nil {
			fmt.Print(err)
		}
		var statement metadata.MetadataStatement
		json.Unmarshal(b, &statement)
		var entry metadata.MetadataTOCPayloadEntry
		entry.AaGUID = statement.AaGUID
		entry.MetadataStatement = statement
		entry.StatusReports = reports
		aaguid, err := uuid.FromString(entry.AaGUID)
		if err != nil {
			fmt.Println(err)
		} else {
			metadata.Metadata[aaguid] = entry
			fmt.Println("Loaded metadata for " + entry.MetadataStatement.Description + ", AAGUID: " + entry.MetadataStatement.AaGUID)
		}
	}
}
