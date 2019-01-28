package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

// Config represents the configuration information.
type Config struct {
	DBName       string `json:"db_name"`
	DBPath       string `json:"db_path"`
	HostAddress  string `json:"host_address"`
	HostPort     string `json:"host_port"`
	LogFile      string `json:"log_file"`
	RelyingParty string `json:"relying_party"`
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
