# Today In AI Daily Image Brief

Use this template after the lead story is verified and before any image generation or compositing.

Before completing it, refresh the Fireship corpus when stale, read `youtube/fireship-today-in-ai-library/04-thumbnail-mechanics.md`, and open both contact sheets under `youtube/fireship-today-in-ai-library/data/contact-sheets/`.

## Mechanism Chosen

- Current contact sheets opened:
- Fireship mechanism being transferred:
- Why it fits this verified event:
- Exact source wording, composition, meme family, pose, and props being avoided:

## Editorial Idea

- Lead claim:
- Important limitation:
- Hook, two to five words:
- Why the hook is accurate:
- Direct actor or product:
- Relationship: who caused, owns, broke, beat, copied, or benefits:
- One visual joke:

## Visual Source

- Kind: `established_meme`, `official_press_asset`, `licensed_asset`, `public_domain_asset`, `owned_asset`, or `generated_original`
- Name:
- Meme family:
- Source page URL:
- Direct asset URL:
- Local asset path:
- Usage or rights note:
- Recognizable traits:
- If `generated_original`, why no established meme or sourced image fits:

Use the real recognizable meme or public-figure asset when the premise fits. Do not ask an image model to make a generic substitute for a known subject. A generated original is the fallback, not the default.

## Production Route

Choose one:

- `reference_generation`: attach the source image and official logos to the built-in image generator so the face, costume, expression, prop, or logo placement becomes one coherent scene.
- `cutout_composite`: remove the source background and integrate the exact cutout with matched light, shadow, grain, edges, and occlusion.
- `generated_original`: use only when no known meme, public figure, official press asset, licensed asset, public-domain asset, or owned asset fits.

- Selected route:
- Why this route will preserve recognition:
- Reference image paths:
- Background-removal plan, if used:
- Lighting and material unification plan:

Reject raw rectangular screenshots, white halos, sticker edges, floating logos, and generic substitute people.

## Composition

- Main composition:
- Subject pose:
- Prop setup:
- Visual joke:
- Text zone:
- Subject zone:
- What remains visible at 288 by 162 pixels:

Use one text idea, one visual idea, and one series mark. Keep the frame simple enough to understand in one glance.

## Typography

- Typeface: `Instrument Sans ExtraBold` or `Instrument Sans Black`
- Weight, at least 800:
- Primary color: `#F7F8F4` or `#FFFFFF`
- Accent color: `#72DFA5`
- Dominant word or phrase:
- Outline or shadow treatment:
- Exact post-generation text-composite plan:

Use no more than three stacked lines. Make one word or short phrase visually dominant. Confirm readability at 288 by 162 pixels.

## AI Mentorship Palette

The designed frame must use:

- Jet Black `#0B0F0D`
- Old Money Green `#0F583D`
- Mint Green `#72DFA5`
- Warm Paper `#F7F8F4`
- White `#FFFFFF`

Natural skin tones, recognizable source-meme colors, and exact official logo colors may remain unchanged. Do not add another designed accent color.

## Publication Mark

Use the exact master:

`today-in-ai/brand/selected/today-in-ai-logo-white-transparent.png`

- Placement: fixed bottom-left series badge
- Canvas: exactly 1920 by 1080 pixels
- Width: exactly 230 pixels
- Left edge: exactly 84 pixels
- Bottom edge: exactly 84 pixels
- Treatment: transparent, no plate, flat, crisp, and identical across editions
- Apply with: `python3 execution/today_in_ai_badge.py --input <base> --output <final>`

Do not generate, redraw, recolor, stretch, or turn the publication mark into a large in-scene sign.

## Official Logos

For every directly relevant company or product logo:

- Brand:
- Official source URL:
- Local asset path:
- Physical or designed surface:
- Perspective and lighting plan:
- Texture, reflection, grain, and occlusion plan:
- Surface containment plan: how every visible logo pixel stays inside the usable face and avoids bevels, seams, gaps, and neighboring objects:

Attach every logo as an image reference when it participates in a face, costume, prop, screen, or in-scene surface. Tell the model not to invent or approximate a mark. If generation changes a logo's shape, lettering, spacing, or color, replace or edit it with the exact official asset and rebuild the material integration.

## Generation Prompt

For `reference_generation`, include these exact constraints:

`Use the supplied reference images for the recognizable subject, meme premise, and official company logos. Preserve the source subject's recognizable identity and the meme's defining pose, expression, crop, and object relationship. Do not invent or approximate any logo. Leave the bottom-left badge area empty. Do not render the Today in AI badge. Use only #0B0F0D, #0F583D, #72DFA5, #F7F8F4, and #FFFFFF for the designed frame. Natural skin tones, source-meme colors, and exact official logo colors may remain unchanged.`

Ask the model to render the coherent subject, transformation, lighting, background, and material integration. Add exact headline type and the locked Today in AI badge after the base visual is approved.

## Final QA

- Exact 1920 by 1080 pixels
- Hook is two to five words and readable at 288 by 162 pixels
- One dominant phrase, one visual premise, one bottom-left series badge
- Real meme or sourced asset remains recognizable
- Reference-aware generation or a professionally integrated background-removed cutout
- Source URLs and usage note are recorded
- AI Mentorship designed palette is exact
- Today in AI master is exact, transparent, 230 pixels wide, 84 pixels from left and bottom
- Official logos are exact, current, and were supplied as references
- Logos match perspective, lighting, texture, reflection, grain, and occlusion
- Every logo pixel stays inside its intended surface and follows that surface's plane
- The mechanism was named, but no Fireship wording, composition, meme family, pose, or prop setup was copied
- No fake interface, generated logo, watermark, or unsupported implication
- Rolling seven-day novelty check passes
