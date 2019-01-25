package server

import "net/http/httptest"

func (ss *ServerSuite) TestGetAssertion() {
	req := httptest.NewRequest("POST", "/assertion", nil)
	response := httptest.NewRecorder()
	ss.server.GetAssertion(response, req)
}
