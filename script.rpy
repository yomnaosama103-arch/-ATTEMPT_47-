
#  ATTEMPT 47  

# ---------- Characters ----------
define dev = Character("Me", color="#7fd1ff")
define lead = Character("Boss", color="#ffb347")
define friend = Character("Sam", color="#9dff9d")

# ---------- Variables ----------
default attempt = 1
default know_test = False
default know_scope = False
default know_rest = False
default lessons = 0
default hint = False

define bounce_period = 1.2
define white_flash = Fade(0.1, 0.0, 0.8, color="#ffffff")
define red_flash = Fade(0.05, 0.0, 0.3, color="#ff0000")

# ---------- Plain color images ----------
image bg white = Solid("#ffffff")
image bg dark = Solid("#14142b")

# ---------- Project assets (filenames matched to your folders) ----------
image bg title = "images/bg title.png"
image bg room = "images/bg room.png"
image bg office = "images/bg office.png"
image bg road = "images/bg road.png"
image bg stage = "images/bg stage.png"
image bg crash = "images/bg crash.png"
image bg win = "images/bg win.png"
image bg secret = "images/bg secret.png"

image ball = "images/ball.png"
image dev normal = "images/dev normal.png"
image dev sad = "images/dev sad.png"
image dev happy = "images/dev happy.png"
image boss normal = "images/boss normal.png"
image boss angry = "images/boss angry.png"
image boss happy = "images/boss happy.png"
image friend normal = "images/friend normal.png"
image friend worried = "images/friend worried.png"

# ---------- Safe helpers (the game will not crash if a sound is missing) ----------
init python:
    def play_sfx(name):
        path = "audio/" + name
        if renpy.loadable(path):
            renpy.sound.play(path)

    def play_music(name):
        path = "audio/" + name
        if renpy.loadable(path):
            renpy.music.play(path, loop=True, fadein=1.0)

    def bounce_h(t):
        # 1.0 = ball at the top, 0.0 = ball touching the floor
        p = (t % bounce_period) / bounce_period
        return (2.0 * p - 1.0) ** 2

# ---------- Animations ----------
transform slide_in_left:
    xalign 0.0 yalign 1.0
    xoffset -400 alpha 0.0
    easein 0.5 xoffset 0 alpha 1.0

transform slide_in_right:
    xalign 1.0 yalign 1.0
    xoffset 400 alpha 0.0
    easein 0.5 xoffset 0 alpha 1.0

transform center_pos:
    xalign 0.5 yalign 1.0

transform hop_left:
    xalign 0.0 yalign 1.0
    yoffset 0
    easeout 0.2 yoffset -60
    easein 0.2 yoffset 0
    easeout 0.1 yoffset -20
    easein 0.1 yoffset 0

transform shake_char:
    xoffset 0
    linear 0.05 xoffset -15
    linear 0.05 xoffset 15
    linear 0.05 xoffset -10
    linear 0.05 xoffset 10
    linear 0.05 xoffset 0

transform glitch:
    alpha 1.0
    linear 0.05 alpha 0.3
    linear 0.05 alpha 1.0
    linear 0.05 alpha 0.5
    linear 0.05 alpha 1.0

# ---------- HUD: attempt + lessons ----------
screen lessons_hud():
    frame:
        xalign 0.98
        yalign 0.02
        padding (20, 10)
        background "#000000aa"
        vbox:
            text "Attempt [attempt]" size 28 color "#ffffff"
            text "Lessons: [lessons]/3" size 28 color "#9dff9d"

# ---------- BOUNCE mini-game ----------
# Click (or press SPACE) when the ball is inside the green zone.
# Catch 3 bounces in 8 seconds to keep a hint for the next attempt.
screen bounce_game():
    modal True
    zorder 100

    default t = 0.0
    default hits = 0
    default misses = 0
    default last_cycle = -1

    $ h = bounce_h(t)
    $ in_zone = h < 0.12
    $ cycle = int(t / bounce_period)
    $ secs_left = max(0, int(8.0 - t))
    $ act = If(in_zone and cycle != last_cycle, [SetScreenVariable("hits", hits + 1), SetScreenVariable("last_cycle", cycle), Function(play_sfx, "sfx_boing.mp3")], [SetScreenVariable("misses", misses + 1), Function(play_sfx, "sfx_miss.mp3")])

    timer 0.03 repeat True action If(hits >= 3, Return(True), If(t >= 8.0, Return(False), SetScreenVariable("t", t + 0.03)))

    add "bg dark"
    add Solid("#2ecc7144") xpos 560 ypos 700 xysize (800, 200)
    add Solid("#ffffff") xpos 560 ypos 900 xysize (800, 6)
    text "BOUNCE ZONE" size 36 color "#9dff9d" xalign 0.5 ypos 910
    add "ball" xalign 0.5 ypos (int(760 - h * 480))

    text "BOUNCE BACK!" size 64 color "#ffb347" xalign 0.5 ypos 40
    text "Bounces: [hits]/3" size 48 color "#ffffff" xalign 0.5 ypos 130
    text "Time: [secs_left]" size 36 color "#cccccc" xalign 0.5 ypos 200
    text "Click or press SPACE when the ball is in the green zone" size 30 color "#aaaaaa" xalign 0.5 ypos 990

    # invisible full-screen button on top: any click counts
    button:
        xfill True
        yfill True
        action act

    key "K_SPACE" action act

# ============================================================
#  GAME START
# ============================================================
label start:
    scene bg title with fade
    $ play_music("music_main.mp3")
    pause 2.5
    show screen lessons_hud
    scene black with fade
    "Game jam deadline: 1 hour left."
    "Your project is almost done... almost."
    jump day_home

# ------------------------------------------------------------
#  STOP 1: HOME  (lesson: test your work)
# ------------------------------------------------------------
label day_home:
    scene bg room with dissolve
    $ lessons = know_test + know_scope + know_rest
    show dev normal at slide_in_left

    if attempt == 1:
        dev "Okay. Almost there. Time to submit."
    elif lessons < 3:
        show dev sad
        dev "Wait... I've been here before. I remember what went wrong."
    else:
        show dev happy at hop_left
        dev "I know exactly what to do this time."

    if hint:
        call show_hint

    $ play_sfx("sfx_click.mp3")
    menu:
        "Submit right now, no testing":
            jump crash_test
        "Panic and rewrite everything":
            jump crash_panic
        "Run the full tests first" if know_test:
            jump day_road
        "Close the laptop and sleep for a while" if attempt >= 5:
            jump secret_end

label crash_test:
    $ play_sfx("sfx_crash.mp3")
    scene bg crash with red_flash
    with vpunch
    show boss angry at slide_in_right
    show dev sad at slide_in_left
    "CRASH! The game won't even launch."
    lead "What happened?!"
    dev "I... didn't test it."
    if not know_test:
        $ know_test = True
        "LESSON LEARNED: Always test before you submit."
    else:
        "You already knew that one. Slow down."
    jump rewind

label crash_panic:
    $ play_sfx("sfx_crash.mp3")
    scene bg crash with hpunch
    show dev sad at center_pos, shake_char
    "You rewrite everything in a panic."
    "Half of it breaks. The clock runs out."
    "Nothing learned this time... except that panic doesn't help."
    jump rewind

# ------------------------------------------------------------
#  STOP 2: THE ROAD  (lesson: ask for help)
# ------------------------------------------------------------
label day_road:
    scene bg road with dissolve
    show dev normal at slide_in_left
    if attempt >= 2:
        show friend worried at slide_in_right
    else:
        show friend normal at slide_in_right

    if attempt == 1:
        friend "Hey! Big day today. You look nervous."
    elif attempt <= 3:
        friend "Weird... I feel like we've had this exact conversation before."
    elif attempt == 4:
        friend "Okay, this is getting creepy. You keep saying the same things."
    else:
        friend "Hey... when was the last time you slept?"

    if hint:
        call show_hint

    dev "I just need to fix one last bug."
    menu:
        "Ignore Sam and code alone on the bus":
            jump crash_rest
        "Stare out the window and give up":
            jump crash_giveup
        "Let Sam help with the bug" if know_rest:
            jump day_stage

label crash_rest:
    scene bg road with dissolve
    show dev sad at center_pos, shake_char
    "You code alone, nonstop..."
    "...and fall asleep. You wake up three stops too late."
    $ play_sfx("sfx_crash.mp3")
    scene bg crash with vpunch
    show boss angry at center_pos
    lead "The deadline was 20 minutes ago!"
    if not know_rest:
        $ know_rest = True
        "LESSON LEARNED: Ask for help. You don't have to do it alone."
    else:
        "You knew you didn't have to do this alone."
    jump rewind

label crash_giveup:
    scene bg crash with hpunch
    show dev sad at slide_in_left
    show friend worried at slide_in_right
    "You stop trying. The deadline passes quietly."
    friend "Hey... don't quit on me. Not yet."
    "No lesson this time. But someone still believes in you."
    jump rewind

# ------------------------------------------------------------
#  STOP 3: THE DEMO  (lesson: cut features)
# ------------------------------------------------------------
label day_stage:
    scene bg stage with dissolve
    $ play_sfx("sfx_tick.mp3")
    show dev normal at slide_in_left
    show boss normal at slide_in_right

    if hint:
        call show_hint

    lead "Alright. You're up. Show us your game."
    dev "The build runs... but one extra feature is still half finished."
    menu:
        "Add one last cool feature":
            jump crash_scope
        "Hide in the bathroom until it's over":
            jump crash_hide
        "Cut the extra feature and present what works" if know_scope:
            jump win_check

label crash_scope:
    $ play_sfx("sfx_crash.mp3")
    scene bg crash with hpunch
    show boss angry at slide_in_right
    show dev sad at slide_in_left
    "You add a fancy feature at the last second."
    "It breaks everything."
    lead "Why would you add that NOW?!"
    if not know_scope:
        $ know_scope = True
        "LESSON LEARNED: Cut features. Finish what you have."
    else:
        "You knew better. Less is more."
    jump rewind

label crash_hide:
    scene bg office with dissolve
    show boss angry at center_pos
    "You hide. Nobody presents. The boss knocks on the door."
    lead "We can hear you breathing in there!"
    "Nothing learned... except that hiding doesn't fix anything."
    jump rewind

# ------------------------------------------------------------
#  REWIND + BOUNCE mini-game
# ------------------------------------------------------------
label rewind:
    $ attempt += 1
    $ lessons = know_test + know_scope + know_rest
    $ play_sfx("sfx_rewind.mp3")
    scene bg white with white_flash
    show dev normal at center_pos, glitch
    "Everything glitches... and goes white."
    "The day starts over."
    call bounce_minigame
    if lessons == 2:
        "One more lesson... and you'll finally get it."
    "You wake up again. Same morning."
    jump day_home

label bounce_minigame:
    scene bg dark with dissolve
    "{b}BOUNCE BACK!{/b} Click or press SPACE when the ball is in the green zone."
    "Catch 3 bounces before time runs out."
    call screen bounce_game
    if _return:
        $ hint = True
        $ play_sfx("sfx_win.mp3")
        "You bounced back! You'll remember a hint."
    else:
        $ hint = False
        "You couldn't catch it... but you'll try again."
    return

label show_hint:
    if not know_test:
        "A faint thought: 'Did I even test it?'"
    elif not know_rest:
        "A faint thought: 'I don't have to do this alone.'"
    elif not know_scope:
        "A faint thought: 'Less is more.'"
    else:
        "A faint thought: 'Trust what you have learned.'"
    $ hint = False
    return

# ------------------------------------------------------------
#  ENDINGS
# ------------------------------------------------------------
label win_check:
    if attempt <= 4:
        jump perfect_end
    else:
        jump persistence_end

label perfect_end:
    hide screen lessons_hud
    $ renpy.music.stop(fadeout=1.0)
    $ play_sfx("sfx_win.mp3")
    $ play_music("music_win.mp3")
    scene bg win with dissolve
    show dev happy at hop_left
    show friend normal at slide_in_right
    friend "You tested it. You cut the extra feature. And I fixed the last bug!"
    dev "We have three minutes left. Let's submit!"
    scene bg stage with dissolve
    show boss happy at center_pos
    lead "Submitted on time? After all that?"
    lead "Nice work. How did you do it?"
    show dev happy at slide_in_left
    dev "Let's just say... I bounced back."
    friend "Funny. I had a feeling we've done this before."
    "ENDING 1 of 3: BOUNCE BACK"
    "Every failure was a lesson. Every lesson was a bounce."
    return

label persistence_end:
    hide screen lessons_hud
    $ renpy.music.stop(fadeout=1.0)
    $ play_sfx("sfx_win.mp3")
    $ play_music("music_win.mp3")
    scene bg win with dissolve
    show dev happy at hop_left
    show friend normal at slide_in_right
    dev "It took me [attempt] attempts. [attempt]!"
    friend "I know. I remember every one. I kept trying to help you."
    scene bg stage with dissolve
    show boss happy at center_pos
    lead "It isn't perfect. But it works. And you didn't quit."
    dev "I fell down a lot. I just kept bouncing."
    "ENDING 2 of 3: THE LONG WAY BACK"
    "It's not about how many times you fall. It's about how many times you get up."
    return

label secret_end:
    hide screen lessons_hud
    $ renpy.music.stop(fadeout=2.0)
    $ play_sfx("sfx_secret.mp3")
    scene bg secret with Dissolve(1.5)
    show dev sad at center_pos
    dev "What if I just... stop? Close the laptop. Sleep."
    show dev happy at center_pos
    "You lie down. For the first time in a very long time, you rest."
    "When you open your eyes, the sun is rising."
    "The counter on the wall flickers."
    "It doesn't say [attempt]. It says 47."
    "You had been looping long before you started counting."
    show friend normal at slide_in_right
    friend "Good morning. Finally."
    dev "The deadline..."
    friend "It can wait. You came back stronger. That's what counts."
    "ENDING 3 of 3 (SECRET): REST IS A BOUNCE TOO"
    "Sometimes bouncing back means taking a break."
    return