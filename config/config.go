package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

// Config represents the configuration information.
type Config struct {
	DBName       string `json:"db_name"`       // DBName is the type of database to use. Right now, only "sqlite3" is supported
	DBPath       string `json:"db_path"`       // DBPath is the name of the database itself.
	HostAddress  string `json:"host_address"`  // HostAddress is the address to listen for connections on.
	HostPort     string `json:"host_port"`     // HostPort is the port to listen on.
	LogFile      string `json:"log_file"`      // LogFile is an optional file to log messages to.
	RelyingParty string `json:"relying_party"` // RelyingParty is the name of the WebAuthn relying party.
}

// LoadConfig loads a configuration at the provided filepath, returning the
// parsed configuration.
func LoadConfig(filepath string) (*Config, error) {
	// Get the config file
	configFile, err := ioutil.ReadFile(filepath)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		return nil, err
	}
	config := &Config{}
	err = json.Unmarshal(configFile, config)
	return config, err
}
