# Inclusive Learning and Shared Display Patterns

## Perceivable live feedback

- Show microphone activity with a live visual level indicator, and label meaningful ambient events in text; learners need confirmation before and beyond transcript output.
- Style interim recognition tokens with compliant contrast plus a non-color distinction such as a dashed underline; faded text fails under projector washout.
- Use a restrained edge flash for success and a localized motion cue for error, and avoid rapid full-screen flashing to reduce seizure risk.
- Pair phonetic text with visual articulation or locally appropriate sign-language support when auditory memory cannot be assumed.

## Stable transcript behavior

- Persist a rolling transcript buffer continuously in local storage or IndexedDB, then restore it on reopen; a manual save cannot protect an active class session.
- Keep final sentences as stable nodes and mutate only the trailing interim span; full-region replacement breaks the learner's visual tracking.
- Auto-scroll only near the bottom, pause it during historical inspection or word lookup, and provide a visible return-to-live action.
- Make inline word actions keyboard-operable with a button role, explicit focus behavior, and a 44px minimum target.

## Classroom geometry

- Keep caption layouts side-by-side on 1024px XGA projectors; defer the narrow stacked breakpoint until roughly 840px or below.
- Offer a high-contrast projector mode with a dark base, bright text, and limited semantic highlights; ambient light weakens gray-on-light treatments.
- Scale captions with `clamp()` and apply `overflow-wrap: break-word`; distance viewing and long unbroken text otherwise create unreadable overflow.
- Support presenter keys for microphone, fullscreen, quiz choices, and dismissal, and hide nonessential chrome in presentation mode after inactivity.
