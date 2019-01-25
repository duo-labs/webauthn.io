package models

import (
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/jinzhu/gorm"
)

// Authenticator is a struct representing a WebAuthn authenticator, which is
// responsible for generating Credentials. For this demo, we map a single
// credential to a single authenticator.
type Authenticator struct {
	gorm.Model
	webauthn.Authenticator
}

// GetAuthenticator returns the authenticator the given id corresponds to. If
// no authenticator is found, an error is thrown.
func GetAuthenticator(id uint) (Authenticator, error) {
	authenticator := Authenticator{}
	err := db.Where("id=?", id).Find(&authenticator).Error
	return authenticator, err
}

// CreateAuthenticator creates a new authenticator that's tied to a Credential.
func CreateAuthenticator(a webauthn.Authenticator) (Authenticator, error) {
	authenticator := Authenticator{}
	authenticator.Authenticator = a
	err = db.Save(&authenticator).Error
	return authenticator, err
}

// UpdateAuthenticatorSignCount updates a specific authenticator's sign count for tracking
// potential clone attempts.
func UpdateAuthenticatorSignCount(id uint, count uint32) error {
	return db.Model(Authenticator{}).Where("id=?", id).Update("sign_count", count).Error
}
