package models

import (
	"encoding/binary"

	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/jinzhu/gorm"
)

// PlaceholderUsername is the default username to use if one isn't provided by
// the user (in the case of a placeholder)
const PlaceholderUsername = "testuser"

// PlaceholderUserIcon is the default user icon used when creating a new user
const PlaceholderUserIcon = "example.icon.duo.com/123/avatar.png"

// User represents the user model.
type User struct {
	gorm.Model
	Username    string       `json:"name" sql:"not null;"`
	DisplayName string       `json:"display_name"`
	Icon        string       `json:"icon,omitempty"`
	Credentials []Credential `json:"credentials,omitempty"`
}

// WebAuthnID returns the user ID as a byte slice
func (u User) WebAuthnID() []byte {
	buf := make([]byte, binary.MaxVarintLen64)
	binary.PutUvarint(buf, uint64(u.ID))
	return buf
}

// WebAuthnName returns the user's username
func (u User) WebAuthnName() string {
	return u.Username
}

// WebAuthnDisplayName returns the user's display name
func (u User) WebAuthnDisplayName() string {
	return u.DisplayName
}

func (u User) WebAuthnIcon() string {
	return u.Icon
}

func (u User) WebAuthnCredentials() []webauthn.Credential {
	// TODO: Should credentials be an interface? I suppose the other
	// option would be to enumerate through them here, converting them as needed.
	wcs := []webauthn.Credential{}
	for _, cred := range u.Credentials {
		wcs = append(wcs, webauthn.Credential{
			ID:            cred.CredentialID,
			PublicKey:     cred.PublicKey,
			Authenticator: cred.WebauthnAuthenticator(),
		})
	}
	return wcs
}

// GetUser returns the user that the given id corresponds to. If no user is found, an
// error is thrown.
func GetUser(id uint) (User, error) {
	u := User{}
	err := db.Where("id=?", id).Preload("Credentials").Find(&u).Error
	if err != nil {
		return u, err
	}
	return u, nil
}

// GetUserByUsername returns the user that the given username corresponds to. If no user is found, an
// error is thrown.
func GetUserByUsername(username string) (User, error) {
	u := User{}
	err := db.Where("username = ?", username).Preload("Credentials").Find(&u).Error

	if err != nil {
		return u, err
	}
	return u, err
}

// PutUser updates the given user
func PutUser(u *User) error {
	if db.NewRecord(&u) {
		log.Debugf("creating new user: %s", u.Username)
	}
	err := db.Save(&u).Error
	return err
}
