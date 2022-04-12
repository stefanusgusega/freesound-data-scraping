"""
Module to connect to FreeSound via Flask
"""
import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from icecream import ic

AUTHORIZATION_BASE_URL = "https://freesound.org/apiv2/oauth2/authorize/"
TOKEN_URL = "https://freesound.org/apiv2/oauth2/access_token/"

# Load the environment variables on .env
load_dotenv()

app = Flask(__name__)


# The information below is obtained upon registration of new Freesound API
# credentials here: http://freesound.org/apiv2/apply
# See documentation of "Step 3" below to understand how to fill in the
# "Callback URL" field when registering the new credentials.
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("API_KEY")


@app.route("/")
def demo():
    """
    Step 1: User Authorization.

    Redirect the user/resource owner to OAuth provider (i.e. FreeSound)
    using an URL with a few key OAuth parameters.
    """
    freesound = OAuth2Session(client_id)
    authorization_url, state = freesound.authorization_url(AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.
    session["oauth_state"] = state
    ic(state)

    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider


@app.route("/callback", methods=["GET"])
def callback():
    """
    Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.

    Note that the URL at which your app is serving this view is the
    'Callback URL' that you have to put in the API credentials you create
    at FreeSound. If running this code example unchanged, the callback URL should be: http://localhost:5000/callback
    """
    freesound = OAuth2Session(client_id, state=session["oauth_state"])
    ic(session["oauth_state"])
    ic(freesound.state)
    ic(request.url)

    token = freesound.fetch_token(
        TOKEN_URL, client_secret=client_secret, authorization_response=request.url
    )
    # If you're using the freesound-python client library to access
    # Freesound, this is the token you should use to make OAuth2 requests
    # You should set the token like:
    #     client.set_token(token ,"oauth")

    # However, for this example lets lets save the token and show how to
    # access a protected resource that will return some info about the user account
    # who has just been authenticated using OAuth2. We redirect to the /profile
    # route of this app which will query Freesound for the user account details.

    session["oauth_token"] = token
    return redirect(url_for(".profile"))


@app.route("/profile", methods=["GET"])
def profile():
    """
    Fetching a protected resource using an OAuth2 token.
    """
    freesound = OAuth2Session(client_id, token=session["oauth_token"])
    return jsonify(
        data=freesound.get("https://freesound.org/apiv2/me").json(),
        token=session["oauth_token"],
    )


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.secret_key = os.urandom(24)
    app.run(debug=True)
