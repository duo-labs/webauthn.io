package models

import "github.com/duo-labs/webauthn/webauthn"

func (ms *ModelsSuite) TestUpdateAuthenticatorSignCount() {
	a := webauthn.Authenticator{
		AAGUID:    []byte("testguid"),
		SignCount: 0,
	}
	authenticator, err := CreateAuthenticator(a)
	ms.Nil(err)
	ms.Equal(authenticator.AAGUID, a.AAGUID)
	ms.Equal(authenticator.SignCount, a.SignCount)

	// Update the sign count, making sure that it's applied
	expected := uint32(5)
	err = UpdateAuthenticatorSignCount(authenticator.ID, expected)
	ms.Nil(err)

	got, err := GetAuthenticator(authenticator.ID)
	ms.Nil(err)
	ms.Equal(got.ID, authenticator.ID)
	ms.Equal(expected, got.SignCount)
}
