package models

import (
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/jinzhu/gorm"
)

// Credential is the stored credential for Auth
type Credential struct {
	gorm.Model

	CredentialID []byte `json:"credential_id"`

	User   User `json:"user"`
	UserID uint `json:"user_id"`

	Authenticator   Authenticator `json:"authenticator"`
	AuthenticatorID uint          `json:"authenticator_id"`

	PublicKey []byte `json:"public_key,omitempty"`
}

func (c *Credential) WebauthnAuthenticator() webauthn.Authenticator {
	return c.Authenticator.Authenticator
}

// CreateCredential creates a new credential object
func CreateCredential(c *Credential) error {
	if db.NewRecord(&c) {
		err = db.Save(&c).Error
		return err
	}
	return err
}

// UpdateCredential updates the credential with new attributes.
func UpdateCredential(c *Credential) error {
	err = db.Save(&c).Error
	return err
}

// GetCredentialsForUser retrieves all credentials for a provided user regardless of relying party.
func GetCredentialsForUser(user *User) ([]Credential, error) {
	creds := []Credential{}
	err := db.Where("user_id = ?", user.ID).Preload("Authenticator").Find(&creds).Error
	return creds, err
}

// GetCredentialForUser retrieves a specific credential for a user.
func GetCredentialForUser(user *User, credentialID string) (Credential, error) {
	cred := Credential{}
	err := db.Where("user_id = ? AND cred_id = ?", user.ID, credentialID).Preload("Authenticator").Find(&cred).Error
	return cred, err
}

// DeleteCredentialByID gets a credential by its ID. In practice, this would be a bad function without
// some other checks (like what user is logged in) because someone could hypothetically delete ANY credential.
func DeleteCredentialByID(credentialID string) error {
	return db.Where("cred_id = ?", credentialID).Delete(&Credential{}).Error
}
