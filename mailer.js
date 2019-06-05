const nodemailer = require('nodemailer');
const { google } = require('googleapis');
const keys = require('./keys');

module.exports = {
  //General function for sending email messages
  sendMail: async (mailParams) => {
 
    const OAuth2 = google.auth.OAuth2;

    const oauth2Client = new OAuth2(
      keys.clientId,
      keys.clientSecret,
      "https://developers.google.com/oauthplayground"
    );
    
    oauth2Client.setCredentials({
      refresh_token: keys.refreshToken,
    });
    
    const tokens =  await oauth2Client.refreshAccessToken();
    const accessToken = tokens.credentials.access_token;
    

    const smtpTransport = nodemailer.createTransport({
      service: keys.service,
      auth: {
        type: keys.type,
        user: keys.user,
        clientId: keys.clientId,
        clientSecret: keys.clientSecret,
        refreshToken: keys.refreshToken,
        accessToken: accessToken
      }
    });
    
   const mailOptions = {
      from: keys.user,
      to: mailParams.to,
      subject: mailParams.subject,
      text: mailParams.text,
      html: mailParams.html,
    };

    smtpTransport.sendMail(mailOptions, (err, res) => {
      if (err) {
        return console.log(err);
      } else {
        return res.response;
      }
    });
  }
};

