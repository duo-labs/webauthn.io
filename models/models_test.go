package models

import (
	"testing"

	"github.com/duo-labs/webauthn.io/config"
	"github.com/stretchr/testify/suite"
)

type ModelsSuite struct {
	config *config.Config
	suite.Suite
}

func (ms *ModelsSuite) SetupSuite() {
	ms.config = &config.Config{
		DBName:      "sqlite3",
		DBPath:      ":memory:",
		HostAddress: "localhost",
	}
	err := Setup(ms.config)
	if err != nil {
		ms.T().Fatalf("Failed creating database: %v", err)
	}
}

func (ms *ModelsSuite) TearDownTest() {
	// Clear database tables between each test. If new tables are
	// used in this test suite they will need to be cleaned up here.
	db.Delete(Credential{})
	db.Delete(SessionData{})

	db.Not("id", 1).Delete(User{})
	db.Model(User{}).Update("name", "admin")

	db.Not("id", ms.config.HostAddress).Delete(RelyingParty{})
}

func TestRunModelsSuite(t *testing.T) {
	suite.Run(t, new(ModelsSuite))
}
