import XMonad
import XMonad.Util.SpawnOnce
import XMonad.Hooks.EwmhDesktops
import XMonad.Hooks.ManageDocks
import XMonad.Hooks.ManageHelpers

import XMonad.Layout.Fullscreen
import XMonad.Layout.NoBorders
import XMonad.Layout.Spacing
import XMonad.Layout.Gaps

import Graphics.X11.ExtraTypes.XF86
import System.Exit
import Control.Monad
import Data.Monoid
import Data.Maybe

import qualified XMonad.StackSet as W
import qualified Data.Map        as M

-- Autostart
myStartupHook = do
	spawn "$HOME/.config/sweetconfigs-xorg/bin/system/autostart"

-- Applications
myTerminal          = "LIBGL_ALWAYS_SOFTWARE=1 kitty -c $HOME/.config/sweetconfigs-xorg/kitty/kitty.conf"

file_manager		= spawn "thunar"
text_editor			= spawn "gedit"
browser			    = spawn "firefox"

-- Menus
launcher 	    	= spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/launcher"
network_menu	    = spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/network"
power_menu 		    = spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/power"
screenshot_menu 	= spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/screenshot"
bluetooth_menu      = spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/bluetooth"
windows_menu 		= spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/window"
run_menu            = spawn "$HOME/.config/sweetconfigs-xorg/bin/rofi/run"

-- Settings
myFocusFollowsMouse 	:: Bool
myFocusFollowsMouse 	= True

myClickJustFocuses 		:: Bool
myClickJustFocuses 		= False

myBorderWidth   		= 2

myFocusedBorderColor 	= "#FFBEBE"
myNormalBorderColor  	= "#DEFBFF"

myModMask       		= mod4Mask

myWorkspaces    		= ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

-- Keybinds
myKeys conf@(XConfig {XMonad.modMask = super}) = M.fromList $

    -- Applications
    [ ((super, xK_Return), 			spawn $ XMonad.terminal conf)

    , ((super .|. shiftMask, 		xK_f), 		file_manager)
    , ((super .|. shiftMask, 		xK_e), 		text_editor)
    , ((super .|. shiftMask, 		xK_w), 		browser)

    -- Menus
    , ((mod1Mask,           		xK_F1), 	launcher)
    , ((super,               		xK_n), 		network_menu)
    , ((super,               		xK_p), 		power_menu)
    , ((super,                     	xK_s), 		screenshot_menu)
    , ((super,                     	xK_b), 		bluetooth_menu)
    , ((super,                     	xK_w), 		windows_menu)
    , ((super,                      xK_r),      run_menu)

    -- Functions
    , ((0,         xF86XK_AudioPlay), 			spawn "mpc toggle")
    , ((0,         xF86XK_AudioPrev), 			spawn "mpc prev")
    , ((0,         xF86XK_AudioNext), 			spawn "mpc next")
    , ((0,         xF86XK_AudioStop), 			spawn "mpc stop")
    , ((0,         xF86XK_AudioRaiseVolume), 	spawn "volume --inc")
    , ((0,         xF86XK_AudioLowerVolume), 	spawn "volume --dec")
    , ((0,         xF86XK_AudioMute), 			spawn "volume --toggle")

    , ((0,         xF86XK_MonBrightnessUp), 	spawn "brightness --inc")
    , ((0,         xF86XK_MonBrightnessDown), 	spawn "brightness --dec") 

    , ((0, 							xK_Print), 	spawn $ "takeshot --now")
    , ((mod1Mask, 					xK_Print), 	spawn $ "takeshot --in5")
    , ((shiftMask, 					xK_Print), 	spawn $ "takeshot --in10")
    , ((controlMask,				xK_Print), 	spawn $ "takeshot --win")
    , ((mod1Mask .|. controlMask  , xK_Print), 	spawn $ "takeshot --area")

    -- Close focused window
    , ((super, 		xK_x), 						kill)
    , ((super, 		xK_Escape), 				spawn "xkill")
    
    -- Lockscreen
    , ((mod1Mask .|. controlMask, 	xK_l), 		spawn "betterlockscreen --lock")

    -- Change gaps on the fly
    , ((super .|. controlMask, 	xK_g), sendMessage $ ToggleGaps)               					-- toggle all gaps
    , ((super .|. shiftMask, 	xK_g), sendMessage $ setGaps [(L,50), (R,50), (U,80), (D,50)]) 	-- reset the GapSpec
    
    , ((super .|. controlMask, 	xK_t), sendMessage $ IncGap 10 L)     -- increment the left-hand gap
    , ((super .|. shiftMask, 	xK_t), sendMessage $ DecGap 10 L)     -- decrement the left-hand gap
    
    , ((super .|. controlMask, 	xK_y), sendMessage $ IncGap 10 U)     -- increment the top gap
    , ((super .|. shiftMask, 	xK_y), sendMessage $ DecGap 10 U)     -- decrement the top gap
    
    , ((super .|. controlMask, 	xK_u), sendMessage $ IncGap 10 D)     -- increment the bottom gap
    , ((super .|. shiftMask, 	xK_u), sendMessage $ DecGap 10 D)     -- decrement the bottom gap

    , ((super .|. controlMask, 	xK_i), sendMessage $ IncGap 10 R)     -- increment the right-hand gap
    , ((super .|. shiftMask, 	xK_i), sendMessage $ DecGap 10 R)     -- decrement the right-hand gap

	-- Window Manager Specific -----------------------------------------

    -- Resize viewed windows to the correct size
    , ((super,                   xK_r), 		refresh)

    -- Move focus to the master window
    , ((super,               	xK_m), 		windows W.focusMaster)

    -- Swap the focused window and the master window
    , ((super,               	xK_s), 		windows W.swapMaster)

    -- Push window back into tiling
    , ((super,               	xK_t),		withFocused $ windows . W.sink)

    -- Rotate through the available layout algorithms
    , ((super,               xK_space), 		sendMessage NextLayout)

    --  Reset the layouts on the current workspace to default
    , ((super .|. shiftMask, xK_space), 		setLayout $ XMonad.layoutHook conf)

    -- Move focus to the next window
    , ((super,                 xK_Tab), 		windows W.focusDown)

    -- Move focus to the next window
    , ((super,               	xK_j), 		windows W.focusDown)
    , ((super,                xK_Left), 		windows W.focusDown)

    -- Move focus to the previous window
    , ((super,               	xK_k), 		windows W.focusUp)
    , ((super,               xK_Right), 		windows W.focusUp)

    -- Swap the focused window with the next window
    , ((super .|. shiftMask, 	xK_j),		windows W.swapDown)
    , ((super .|. shiftMask, 	xK_Left),	windows W.swapDown)

    -- Swap the focused window with the previous window
    , ((super .|. shiftMask, 	xK_k),		windows W.swapUp)
    , ((super .|. shiftMask, 	xK_Right),	windows W.swapUp)

    -- Shrink the master area
    , ((super,               	xK_h),		sendMessage Shrink)
    , ((super .|. controlMask,   xK_Left),	sendMessage Shrink)

    -- Expand the master area
    , ((super,               	xK_l),		sendMessage Expand)
    , ((super .|. controlMask,   xK_Right),	sendMessage Expand)

    -- Increment the number of windows in the master area
    , ((super, 					xK_comma),		sendMessage (IncMasterN 1))

    -- Deincrement the number of windows in the master area
    , ((super,					xK_period),		sendMessage (IncMasterN (-1)))

    -- Restart xmonad
    , ((super, 						 xK_q),		spawn "xmonad --recompile; xmonad --restart")

    ]
    ++

	-- Workspace Specific ---------------------------------------------------------------

    -- mod-[1..9], Switch to workspace N
    -- mod-shift-[1..9], Move client to workspace N
    [((m .|. super, k), windows $ f i)
        | (i, k) <- zip (XMonad.workspaces conf) [xK_1,xK_2,xK_3,xK_4,xK_5,xK_6,xK_7,xK_8,xK_9,xK_0]
        , (f, m) <- [(W.greedyView, 0), (W.shift, shiftMask)]]
    ++

    -- mod-{y,u,i}, Switch to physical/Xinerama screens 1, 2, or 3
    -- mod-shift-{y,u,i}, Move client to screen 1, 2, or 3
    [((m .|. super, key), screenWorkspace sc >>= flip whenJust (windows . f))
        | (key, sc) <- zip [xK_y, xK_u, xK_i] [0..]
        , (f, m) <- [(W.view, 0), (W.shift, shiftMask)]]

-- ## Mouse Bindings ## ------------------------------------------------------------------
myMouseBindings (XConfig {XMonad.modMask = super}) = M.fromList $

    -- mod-button1, Set the window to floating mode and move by dragging
    [ ((super, button1), (\w -> focus w >> mouseMoveWindow w
                                       >> windows W.shiftMaster))

    -- mod-button2, Raise the window to the top of the stack
    , ((super, button2), (\w -> focus w >> windows W.shiftMaster))

    -- mod-button3, Set the window to floating mode and resize by dragging
    , ((super, button3), (\w -> focus w >> mouseResizeWindow w
                                       >> windows W.shiftMaster))
    ]

-- ## Layouts ## -------------------------------------------------------------------------
myLayout = avoidStruts(tiled ||| Mirror tiled ||| Full)
	where
		-- default tiling algorithm partitions the screen into two panes
		tiled   = Tall nmaster delta ratio

		-- The default number of windows in the master pane
		nmaster = 1

		-- Default proportion of screen occupied by master pane
		ratio   = 1/2

		-- Percent of screen to increment by when resizing panes
		delta   = 3/100

-- ## Window rules ## --------------------------------------------------------------------
myManageHook = composeAll . concat $
    [ [isDialog --> doCenterFloat]
    , [className =? c --> doCenterFloat | c <- myCFloats]
    , [title =? t --> doCenterFloat | t <- myTFloats]
    , [resource =? r --> doFloat | r <- myRFloats]
    , [resource =? i --> doIgnore | i <- myIgnores]
    ]
    where
		myCFloats = ["alacritty-float", "MPlayer", "mpv",
					"Gimp", "feh", "Viewnior", "Gpicview",
					"Kvantum Manager", "qt5ct", "VirtualBox Manager", "qemu", "Qemu-system-x86_64",
					"Lxappearance", "Nitrogen", "Arandr", "Pavucontrol", "Xfce4-power-manager-settings", "Nm-connection-editor"]
		myTFloats = ["Downloads", "Save As...", "About : Aditya Shakya", "Getting Started"]
		myRFloats = []
		myIgnores = ["desktop_window"]

-- ## Event handling ## -------------------------------------------------------------------
myEventHook = ewmhDesktopsEventHook

-- ## Logging ## --------------------------------------------------------------------------
myLogHook = return ()

-- ## Main Function ## --------------------------------------------------------------------

-- Run xmonad with all the configs we set up.
main = xmonad $ fullscreenSupport $ docks $ ewmh defaults

defaults = def {
      -- configs
        terminal           = myTerminal,
        focusFollowsMouse  = myFocusFollowsMouse,
        clickJustFocuses   = myClickJustFocuses,
        borderWidth        = myBorderWidth,
        modMask            = myModMask,
        workspaces         = myWorkspaces,
        normalBorderColor  = myNormalBorderColor,
        focusedBorderColor = myFocusedBorderColor,

      -- key bindings
        keys               = myKeys,
        mouseBindings      = myMouseBindings,

      -- hooks, layouts
		manageHook = myManageHook,
        layoutHook = gaps [(L,0), (R,0), (U,0), (D,0)] $ spacingRaw False (Border 10 0 10 0) True (Border 0 10 0 10) True $ myLayout,
        handleEventHook    = myEventHook,
        logHook            = myLogHook,
        startupHook        = myStartupHook
    }
