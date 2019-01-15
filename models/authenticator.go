package models

import (
	log "github.com/duo-labs/webauthn.io/logger"
	"github.com/duo-labs/webauthn/webauthn"
	"github.com/jinzhu/gorm"
)

type Authenticator struct {
	gorm.Model
	webauthn.Authenticator
}

func GetOrCreateAuthenticator(a webauthn.Authenticator) (Authenticator, error) {
	authenticator := Authenticator{}
	err := db.Where("aa_guid=?", a.AAGUID).First(&authenticator).Error
	if err == nil {
		return authenticator, nil
	}
	if err != gorm.ErrRecordNotFound {
		log.Errorf("error finding authenticator: %v", err)
		return authenticator, err
	}
	authenticator.Authenticator = a
	err = db.Debug().Save(&authenticator).Error
	return authenticator, err
}
