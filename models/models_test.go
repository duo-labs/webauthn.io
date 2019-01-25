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
	ms.Nil(err)
}

func (ms *ModelsSuite) TearDownTest() {
	// Clear database tables between each test. If new tables are
	// used in this test suite they will need to be cleaned up here.
	db.Delete(Credential{})
	db.Delete(Authenticator{})

	db.Not("id", 1).Delete(User{})
	db.Model(User{}).Update("name", "admin")

}

func TestRunModelsSuite(t *testing.T) {
	suite.Run(t, new(ModelsSuite))
}
