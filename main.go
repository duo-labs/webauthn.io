package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/duo-labs/webauthn.io/config"
	"github.com/duo-labs/webauthn.io/models"
	"github.com/duo-labs/webauthn.io/server"
)

func main() {
	config, err := config.LoadConfig("config.json")
	if err != nil {
		log.Fatal(err)
	}

	err = models.Setup(config)
	if err != nil {
		log.Fatal(err)
	}

	server := server.NewServer(config)
	go server.Start()

	// Handle graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, syscall.SIGTERM)
	signal.Notify(c, syscall.SIGINT)

	<-c
	log.Println("Shutting down...")
	server.Shutdown()
}
