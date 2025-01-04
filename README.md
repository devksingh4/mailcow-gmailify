# mailcow-gmailify
Tweaks to enable secure and consistent Mailcow -> Gmail forwarding.

## Motivation

I use mailcow as a secure forwarder to my Gmail account. Thus, there's a few functional requirements:

* All emails are ARC-signed before being forwarded to Gmail via Sieve.
* Gmail retrieves all emails via POP3, ignoring duplicate messages and saving new messages
  * This is to ensure that any messages marked as Spam by either Gmail or Mailcow still get delivered into the Spam folder
* Since Sieve requeues the message, a milter must be used to ensure that the return path does not point to the mailbox on Mailcow, but rather to the original sender.


Note that although the SPF check fails, the DKIM/DMARC signature still works so mail deliverability works fine. In the event Gmail were to for some reason reject the message, it would be retrieved via POP anyway. 

This follows much of the same approach as (Open)Gmailify: docs [here](https://www.gmailify.com/docs).

# Usage

## On the Server

1. Add the `milter/` folder to the root of your Mailcow folder (usually `/opt/mailcow-dockerized`).
2. Add/merge the `docker-compose.override.yml` file in the root of your Mailcow folder.
3. Add the lines from extra.cf into `MAILCOW_ROOT/data/conf/postfix/extra.cf`.
4. Run `docker compose build custom-reject-mailcow && docker compose up custom-reject-mailcow -d && docker compose restart postfix-mailcow`

## In the Mailcow Admin UI
1. Ensure that the basics for the domain are setup (SPF/DKIM/DMARC) per Mailcow instructions.
2. Create a new Mailbox template as shown below:

<img width="1568" alt="image" src="https://github.com/user-attachments/assets/16da2e8c-7c88-4bf8-bbcf-1d1210f7dea3" />

3. Create a new mailbox that represents the main forwarded email, using this new template. Generate a long, secure password (this is how Gmail will communicate with Mailcow, you won't use it.)
4. Go to Filters and add the following **Sieve prefilter** for the mailbox and save:
```
require "fileinto";
require "editheader";

if header :contains "X-Spam-Flag" "YES" {
	fileinto "INBOX";
	stop;
}
addheader "X-Gmail-Forwarded" "YES";
redirect "<YOUR GMAIL ADDRESS HERE>";
fileinto "INBOX";
keep;
```

5. Add these credentials to Gmail's "Check mail from other accounts", making sure that Gmail **does not leave email on the server after retrieving**.
6. Also add these credentials to Gmail's "Send mail as" section.



