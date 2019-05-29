const nodemailer = require('nodemailer');
const keys = require('./keys');

const auth = {
  type: 'OAuth2',
  user: keys.smtpUser,
  clientId: keys.smtpClientId,
  clientSecret: keys.smtpClientSecret,
  refreshToken: keys.smtpRefreshToken
};

const transporter = nodemailer.createTransport({
  host: keys.smtpHost,
  port: keys.smtpPort,
  secure: true,
  auth: auth
});

module.exports = {
  //General function for sending email messages
  sendMail: async (mailParams) => {
    const mailOptions = {
      from: 'infield.advantage.support@lthia.org',
      to: mailParams.to,
      subject: mailParams.subject,
      text: mailParams.text,
      html: mailParams.html,
    };

    transporter.sendMail(mailOptions, (err, res) => {
      if (err) {
        return console.log(err);
      } else {
        return res.response;
      }
    });
  }
};

