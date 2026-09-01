# Givvy shared reward-shell bootstrap

## Reusable lesson
When a specific Givvy title is missing its APK, do not stop at the marketing page. A sibling Givvy artifact can still recover the real shell boundaries: crypto, header shape, request order, and the claim oracle.

## What proved reusable
A public Lucky Scratch Card automation repo exposed enough family behavior to recover a live shell baseline:
- app-side encryption: AES-ECB with `MD5("appWorldKey")`
- config-side encryption: AES-ECB with a separate fixed 16-byte key
- app host shape: per-title Heroku host
- shared config host: `givvy-general-config.herokuapp.com`
- request order:
  1. `loginEstablished`
  2. `sendForegroundStatus`
  3. `getStatus`
  4. short delay
  5. `getPresentReward`

## Live verification
The family shell was replayed successfully against the Lucky Scratch specimen host.

Verified facts:
- the same `deviceId` reopens the same account
- a different `deviceId` creates a different account
- `sendForegroundStatus` and `getStatus` return live anti-abuse / ad-provider config
- the full replay produced a real claim oracle with earned credits and balance movement

One proved reward result:
- `statusCode: 200`
- `earnCredits: 1703` in one clean replay
- `userBalanceDouble: "0.0017"`

## Why this matters
This turns a missing-APK target from `blocked` into `partially mappable`.

Even before the target APK is found, you can still:
- recover the family protocol
- verify whether claim replay is real or fake
- identify which missing values are truly target-specific
- prepare a generic probe/client so the target can be tested quickly once its host/package/version are known

## Boundary rule
Do not overclaim from family success.

A working sibling shell does **not** prove another Givvy title is claimable until its own values are tied down:
- real app artifact or hardcoded constants
- real backend host
- real package name and version
- target-specific claim oracle

## Practical operator move
Keep a generic probe ready.

In this workspace the reusable probe is:
- `projects/givvy-shell/givvy_family_probe.py`

Once a new Givvy title is acquired, bind that probe to the title-specific host/package/version first, then demand a real target-side claim response before saying `autoclaim works`.
