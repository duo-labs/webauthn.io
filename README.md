<p align="center">
<img src="https://github.com/duo-labs/webauthn.io/blob/master/static/dist/images/header-illi.png?raw=true" height="400"/>
</p>

## About

This is the source code for [webauthn.io](https://webauthn.io), a demonstration of the Web Authentication specification, or WebAuthn.

This server provides a simple reference implementation of how to add WebAuthn to an application using the [`duo-labs/webauthn`](https://github.com/duo-labs/webauthn) Go library.

## Installation

### Using Docker

The easiest way to start a local instance of webauthn.io is to use the image on Docker Hub:

```
docker run --rm -p 9005:9005 duolabs/webauthn.io
```

To run a local instance of webauthn.io in a Docker container, start by building the container image:

```
docker build -t webauthn.io .
```

Then, run the container, exposing port 9005:

```
docker run --rm -p 9005:9005 webauthn.io
```

After the container launches, you can navigate to localhost:9005 to see the application.

### Building from Source

To get started using a local instance of webauthn.io, first download the source code using:

```
go get github.com/duo-labs/webauthn.io
```

Then, edit `config.json` as needed.

Finally, build and run the application with `go build; ./webauthn.io`)


## More Information

For more information on how WebAuthn works, we recommend checking out [webauthn.guide](https://webauthn.guide).

### License

```
BSD 3-Clause License

Copyright (c) 2019, Duo Labs
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```