# Finding-class exclusions: check the class before you draft

A vulnerability that reproduces perfectly is still worth $0 if the program
excludes its class. This file is the working taxonomy and the order to check it
in. Everything here is verified against the cached policies of the open, paying
programs.

## Check order

1. Program-level `offers_bounties` + `submission_state`.
2. The policy header for a payment retraction ("no monetary", "suspended our
   paid bounty", "reputation only").
3. Per-asset `eligible_for_bounty` in `structured_scopes` — an asset can be
   ineligible while the program flag is true.
4. The out-of-scope list, matched against the finding's class (table below).
5. Any clause about *process* — code-analysis-only, AI-generated, unvalidated.

Steps 4 and 5 are the ones people skip, and they are where whole classes of
findings die.

## Classes most often excluded, and the language that excludes them

| Class | Exclusion language to grep for | Seen in |
|---|---|---|
| Open redirect / URL redirect | "phishing … not in scope", "text injection", "social engineering", "low impact site is not in scope" | WordPress |
| Hard-coded key/secret from an app binary | "hardcoded keys, tokens … extracted from mobile app binaries (APK/IPA)", unless chained to cross-user impact | Basecamp |
| Mobile hard-coded third-party secrets | "Sentry, Twitter, Crashlytics, Firebase, or Branch" | Reddit |
| Hard-coded credentials generally | "hardcoded credentials", "cleartext credentials … excluding API keys" | OKG, Netflix (public sample/test code) |
| Hard-coded values without privilege gain | "hardcoded keys or values, if they do not provide functionality beyond the normal application" | MoonPay |
| Secrets found in a public repo | "mentions of secrets, access tokens, API keys … in Github, will be considered out of scope without proof that they are in-use" | Chainlink |
| Anything already public in open-source code | "information disclosure … including anything already public in our open-source code" | Matomo |
| Code-analysis-only or AI findings | "reports based solely on code analysis, automated tools, or AI-generated output without demonstrated exploitability will not be accepted" | Matomo |
| Missing headers / clickjacking / version disclosure | "lack of an HTTP security header … not in scope", "clickjacking with a minimal security implication", "version number disclosure is not in scope" | WordPress |
| DoS | "denial of service … out of scope" | Nextcloud, WordPress |
| Scanner output | "output of automated scanners without explanation", "reports as such will be closed as N/A" | Basecamp, Vimeo, Razorpay |
| Theoretical impact | "a theoretical vulnerability where you can't demonstrate a significant security impact with a PoC is not in scope" | WordPress |

The right response to an exclusion is not to abandon the finding — it is to find
the *chain* the program asks for, or to record it as a negative and move the
budget to a program that pays for that class.

## Two shapes that kill a static-only finding

Both are increasingly common and both mean the same thing: a local PoC is not
enough, the bug must be shown live.

- "Reports based solely on code analysis … without demonstrated exploitability
  will not be accepted" — the finding needs a live reproduction, not a harness.
- "Already public in our open-source code is out of scope" — a secret or flaw
  visible in a public repo needs proof of *use in production* (a deployment
  fingerprint, a live endpoint, a response) to qualify.

## Turning a blocked finding into a submittable one

A finding blocked only on production evidence usually needs exactly one
authorised request against the live asset. Do not let the pipeline make it:

1. Name the request precisely (method, path, the recovered value, and why it is
   read-only or harmless).
2. State both outcomes and what each means for severity.
3. Ask the human to authorise it, then capture the request/response pair as
   evidence.

Example shapes of that decision: submitting a recovered default credential to
an exposed endpoint (403 = production overrode it, low; accepted = the guarded
command really runs, high), or loading the vulnerable page in a real browser
behind a bot wall (use the site's own verification control; never solve or
automate the challenge).

## Redeeming a finding whose class is excluded

Several programs accept the same finding if it is chained: Basecamp takes a
hard-coded APK key "unless chained with a demonstrated cross-user impact",
Chainlink takes a GitHub secret if you prove it is in use in production. Before
writing a negative, re-read the exclusion for its conditional clause — the
"unless" is the work item.
