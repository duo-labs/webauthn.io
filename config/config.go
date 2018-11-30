package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

// Config represents the configuration information.
type Config struct {
	DBName         string `json:"db_name"`
	DBPath         string `json:"db_path"`
	MigrationsPath string `json:"migrations_prefix"`
	HostAddress    string `json:"host_address"`
	HostPort       string `json:"host_port"`
	HasProxy       bool   `json:"has_proxy"`
}

// Version represents the current version of the software.
var Version = "0.3"

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
	if err != nil {
		return nil, err
	}
	config.MigrationsPath = config.MigrationsPath + config.DBName
	return config, nil
}
