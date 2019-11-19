function detectWebAuthnSupport() {
    if (window.PublicKeyCredential === undefined ||
        typeof window.PublicKeyCredential !== "function") {
        $('#register-button').attr("disabled", true);
        $('#login-button').attr("disabled", true);
        var errorMessage = "Oh no! This browser doesn't currently support WebAuthn."
        if (window.location.protocol === "http:" && (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1")){
            errorMessage = "WebAuthn only supports secure connections. For testing over HTTP, you can use the origin \"localhost\"."
        }
        showErrorAlert(errorMessage);
        return;
    }
}

function string2buffer(str) {
    return (new Uint8Array(str.length)).map(function (x, i) {
        return str.charCodeAt(i)
    });
}

// Encode an ArrayBuffer into a base64 string.
function bufferEncode(value) {
    return base64js.fromByteArray(value)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=/g, "");
}

// Don't drop any blanks
// decode
function bufferDecode(value) {
    return Uint8Array.from(atob(value), c => c.charCodeAt(0));
}

function buffer2string(buf) {
    let str = "";
    if (!(buf.constructor === Uint8Array)) {
        buf = new Uint8Array(buf);
    }
    buf.map(function (x) {
        return str += String.fromCharCode(x)
    });
    return str;
}

var state = {
    createResponse: null,
    publicKeyCredential: null,
    credential: null,
    user: {
        name: "testuser@example.com",
        displayName: "testuser",
    },
}

function setUser() {
    username = $("#input-email").val();
    state.user.name = username.toLowerCase().replace(/\s/g, '');
    state.user.displayName = username.toLowerCase();
}

function checkUserExists() {
    $.get('/user/' + state.user.name + '/exists', {}, null, 'json')
        .done(function (response) {
            return true;
        }).catch(function () {
            return false;
        });
}

function getCredentials() {
    $.get('/credential/' + state.user.name, {}, null, 'json')
        .done(function (response) {
            console.log(response)
        });
}

function makeCredential() {
    hideErrorAlert();
    console.log("Fetching options for new credential");
    if ($("#input-email").val() === "") {
        showErrorAlert("Please enter a username");
        return;
    }
    setUser();
    var credential = null;

    var attestation_type = $('#select-attestation').find(':selected').val();
    var authenticator_attachment = $('#select-authenticator').find(':selected').val();
    
    var user_verification = $('#select-verification').find(':selected').val();
    var resident_key_requirement = $('#select-residency').find(':selected').val();
    var txAuthSimple_extension = $('#extension-input').val();

    $.get('/makeCredential/' + state.user.name, {
            attType: attestation_type,
            authType: authenticator_attachment,
            userVerification: user_verification,
            residentKeyRequirement: resident_key_requirement,
            txAuthExtension: txAuthSimple_extension,
        }, null, 'json')
        .done(function (makeCredentialOptions) {            
            makeCredentialOptions.publicKey.challenge = bufferDecode(makeCredentialOptions.publicKey.challenge);
            makeCredentialOptions.publicKey.user.id = bufferDecode(makeCredentialOptions.publicKey.user.id);
            if (makeCredentialOptions.publicKey.excludeCredentials) {
                for (var i = 0; i < makeCredentialOptions.publicKey.excludeCredentials.length; i++) {
                    makeCredentialOptions.publicKey.excludeCredentials[i].id = bufferDecode(makeCredentialOptions.publicKey.excludeCredentials[i].id);
                }
            }
            console.log("Credential Creation Options");
            console.log(makeCredentialOptions);
            navigator.credentials.create({
                publicKey: makeCredentialOptions.publicKey
            }).then(function (newCredential) {
                console.log("PublicKeyCredential Created");
                console.log(newCredential);
                state.createResponse = newCredential;
                registerNewCredential(newCredential);
            }).catch(function (err) {
                console.info(err);
            });
        });
}

// This should be used to verify the auth data with the server
function registerNewCredential(newCredential) {
    // Move data into Arrays incase it is super long
    let attestationObject = new Uint8Array(newCredential.response.attestationObject);
    let clientDataJSON = new Uint8Array(newCredential.response.clientDataJSON);
    let rawId = new Uint8Array(newCredential.rawId);

    $.ajax({
        url: '/makeCredential',
        type: 'POST',
        data: JSON.stringify({
            id: newCredential.id,
            rawId: bufferEncode(rawId),
            type: newCredential.type,
            response: {
                attestationObject: bufferEncode(attestationObject),
                clientDataJSON: bufferEncode(clientDataJSON),
            },
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            $("#login-button").popover('show')
        }
    });
}

function addUserErrorMsg(msg) {
    if (msg === "username") {
        msg = 'Please add username';
    } else {
        msg = 'Please add email';
    }
    document.getElementById("user-create-error").innerHTML = msg;
}

function getAssertion() {
    hideErrorAlert();
    if ($("#input-email").val() === "") {
        showErrorAlert("Please enter a username");
        return;
    }
    setUser();
    $.get('/user/' + state.user.name + '/exists', {}, null, 'json').done(function (response) {
            console.log(response);
        }).then(function () {
            
            var user_verification = $('#select-verification').find(':selected').val();            
            var txAuthSimple_extension = $('#extension-input').val();

            $.get('/assertion/' + state.user.name, {
                userVer: user_verification,
                txAuthExtension: txAuthSimple_extension
            }, null, 'json')
                .done(function (makeAssertionOptions) {
                    console.log("Assertion Options:");
                    console.log(makeAssertionOptions);
                    makeAssertionOptions.publicKey.challenge = bufferDecode(makeAssertionOptions.publicKey.challenge);
                    makeAssertionOptions.publicKey.allowCredentials.forEach(function (listItem) {
                        listItem.id = bufferDecode(listItem.id)
                    });
                    console.log(makeAssertionOptions);
                    navigator.credentials.get({
                            publicKey: makeAssertionOptions.publicKey
                        })
                        .then(function (credential) {
                            console.log(credential);
                            verifyAssertion(credential);
                        }).catch(function (err) {
                            console.log(err.name);
                            showErrorAlert(err.message);
                        });
                });
        })
        .catch(function (error) {
            if (!error.exists) {
                showErrorAlert("User not found, try registering one first!");
            }
            return;
        });
}

function verifyAssertion(assertedCredential) {
    // Move data into Arrays incase it is super long
    console.log('calling verify')
    let authData = new Uint8Array(assertedCredential.response.authenticatorData);
    let clientDataJSON = new Uint8Array(assertedCredential.response.clientDataJSON);
    let rawId = new Uint8Array(assertedCredential.rawId);
    let sig = new Uint8Array(assertedCredential.response.signature);
    let userHandle = new Uint8Array(assertedCredential.response.userHandle);
    $.ajax({
        url: '/assertion',
        type: 'POST',
        data: JSON.stringify({
            id: assertedCredential.id,
            rawId: bufferEncode(rawId),
            type: assertedCredential.type,
            response: {
                authenticatorData: bufferEncode(authData),
                clientDataJSON: bufferEncode(clientDataJSON),
                signature: bufferEncode(sig),
                userHandle: bufferEncode(userHandle),
            },
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (response) {
            window.location = "/dashboard"
            console.log(response)
        }
    });
}

function setCurrentUser(userResponse) {
    state.user.name = userResponse.name;
    state.user.displayName = userResponse.display_name;
}

function showErrorAlert(msg) {
    $("#alert-msg").text(msg)
    $("#alert").show();
}

function hideErrorAlert() {
    $("#alert").hide();
}

function popoverPlacement(context, source) {
    if ($(window).width() < 992) {
        return "bottom"
    }
    return "right";
}

$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        trigger: 'manual',
        container: 'body',
        placement: popoverPlacement
    })
})