FROM golang:alpine AS build-env
RUN apk add git build-base
WORKDIR /go/src/github.com/duo-labs/webauthn.io
COPY . .
RUN go get -d -v ./...
RUN go build -o webauthn.io

FROM alpine
WORKDIR /opt/webauthn.io
COPY --from=build-env /go/src/github.com/duo-labs/webauthn.io/webauthn.io /opt/webauthn.io/webauthn.io
COPY ./static/dist static/dist
COPY ./templates templates/
COPY ./config.json config.json
RUN sed -i 's/127.0.0.1/0.0.0.0/' config.json
EXPOSE 9005
ENTRYPOINT ./webauthn.io