#!/usr/bin/env python

import gi

gi.require_version('NM', '1.0')
from locale import getpreferredencoding
from os import environ, path
from pathlib import Path
from shlex import split
from shutil import which
from struct import pack
from subprocess import DEVNULL, run
from sys import path as spath
from time import sleep
from uuid import uuid4

from gi.repository import NM, GLib

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import (check_installed, config, notify,  # type: ignore
                   path_expander)


def command(num_lines: int, promt='Networks', active_lines=None, **kwargs) -> list:
    parameters = {
        'rofi': ['-dmenu', '-p', promt, '-l', f'{num_lines}'],
        'wofi': ['--dmenu', '-p', promt, '--lines', f'{num_lines}', '--gtk-dark',
                 '--conf', kwargs.get('config', ''),
                 '--style', kwargs.get('style', ''),
                 '--color', kwargs.get('color', '')]
    }
    highlight, obscure = (
        network.get('rofi_highlight', 'true'),
        network.get('obscure', 'true')
    )

    if highlight is True and app == 'rofi' and active_lines:
        cmd.extend(['-a', ','.join([str(num) for num in active_lines])])
    if promt == 'Passphrase' and obscure is True:
        pass_prompts = {
            'rofi': ['-password'],
            'wofi': ['-P']
        }
        cmd.extend(pass_prompts.get(app))  # type: ignore
    if app == 'rofi' or 'wofi':
        cmd.extend(parameters.get(app))  # type: ignore
    else:
        exit(1)
    return cmd


def passer(rconf: str):
    if app == 'rofi' and rconf.endswith('rasi'):
        return cmd.extend(['-theme', rconf])
    return cmd.extend([])


def choose_adapter(client):
    devices = client.get_devices()
    devices = [i for i in devices if i.get_device_type() == NM.DeviceType.WIFI]
    device_names = '\n'.join([d.get_iface() for d in devices])

    if not devices:
        return None
    if len(devices) == 1:
        return devices[0]
    match app:
        case 'rofi':
            sel = run(command(len(devices),
                              promt='Choose Adapter',
                              config=passer(path_expander(conf))),
                      capture_output=True,
                      check=False,
                      env=env,
                      encoding=enc,
                      input=device_names).stdout
        case 'wofi':
            sel = run(command(len(devices),
                              promt='Choose Adapter',
                              config=path_expander(conf),
                              style=path_expander(style),
                              color=path_expander(color)),
                      capture_output=True,
                      check=False,
                      env=env,
                      encoding=enc,
                      input=device_names).stdout
        case _:
            exit(1)

    if not sel.rstrip():
        exit(1)
    devices = [i for i in devices if i.get_iface() == sel.rstrip()]
    assert len(devices) == 1
    return devices[0]


def bluetooth_get_enabled():
    for bluetooth_path in Path('/sys/class/rfkill/').glob('rfkill'):
        if (bluetooth_path / 'type').read_text().strip() == 'bluetooth':
            return (bluetooth_path / 'soft').read_text().strip() == '0'
    return None


def create_other_actions(client):
    networking_enabled = client.networking_get_enabled()
    networking_action = 'Disable' if networking_enabled else 'Enable'

    wifi_enabled = client.wireless_get_enabled()
    wifi_action = 'Disable' if wifi_enabled else 'Enable'

    bluetooth_enabled = bluetooth_get_enabled()
    bluetooth_action = 'Disable' if bluetooth_enabled else 'Enable'

    actions = [Action(f'{wifi_action} Wifi', toggle_wifi,
                      not wifi_enabled),
               Action(f'{networking_action} Networking',
                      toggle_networking, not networking_enabled)]
    if bluetooth_enabled is not None:
        actions.append(Action(f'{bluetooth_action} Bluetooth',
                              toggle_bluetooth, not bluetooth_enabled))
    actions += [Action('Launch Connection Manager', launch_connection_editor),
                Action('Delete a Connection', delete_connection)]
    if wifi_enabled:
        actions.append(Action('Rescan Wifi Networks', rescan_wifi))
    return actions


def rescan_wifi():
    delay = network.get('rescan_delay', '0')
    for dev in CLIENT.get_devices():
        if gi.repository.NM.DeviceWifi == type(dev):
            try:
                dev.request_scan_async(None, rescan_cb, None)
                loop.run()
                sleep(delay)
                notify(
                    app=notify_app,
                    summary='Wifi',
                    body='Wifi rescan complete',
                    icon=notify_icon,
                    urgent=1
                )
                main()
            except gi.repository.GLib.Error as err:
                notify(
                    app=notify_app,
                    summary='Wifi',
                    body='Wifi rescan failed',
                    icon=notify_icon,
                    urgent=2
                )
                if not err.code == 6:  # pylint: disable=no-member
                    raise err


def rescan_cb(dev, res, data):
    if dev.request_scan_finish(res) is True:
        notify(
            app=notify_app,
            summary='Wifi',
            body='Wifi scan running...',
            icon=notify_icon,
            urgent=0
        )
    else:
        notify(
            app=notify_app,
            summary='Wifi',
            body='Wifi scan failed',
            icon=notify_icon,
            urgent=2
        )
    loop.quit()


def ssid_to_utf8(nm_ap):
    ssid = nm_ap.get_ssid()
    if not ssid:
        return ''
    ret = NM.utils_ssid_to_utf8(ssid.get_data())
    return ret


def prompt_saved(saved_cons):
    actions = create_saved_actions(saved_cons)
    sel = get_selection(actions)
    sel()


def ap_security(nm_ap):
    flags = nm_ap.get_flags()
    wpa_flags = nm_ap.get_wpa_flags()
    rsn_flags = nm_ap.get_rsn_flags()
    sec_str = ''
    if ((flags & getattr(NM, '80211ApFlags').PRIVACY) and
            (wpa_flags == 0) and (rsn_flags == 0)):
        sec_str = ' WEP'
    if wpa_flags:
        sec_str = ' WPA1'
    if rsn_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_PSK:
        sec_str += ' WPA2'
    if rsn_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_SAE:
        sec_str += ' WPA3'
    if ((wpa_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_802_1X) or
            (rsn_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_802_1X)):
        sec_str += ' 802.1X'
    if ((wpa_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_OWE) or
            (rsn_flags & getattr(NM, '80211ApSecurityFlags').KEY_MGMT_OWE)):
        sec_str += " OWE"

    if sec_str == '':
        sec_str = '--'
    return sec_str.lstrip()


class Action:
    def __init__(self,
                 name,
                 func,
                 args=None,
                 active=False):
        self.name = name
        self.func = func
        self.is_active = active
        if args is None:
            self.args = None
        elif isinstance(args, list):
            self.args = args
        else:
            self.args = [args]

    def __str__(self):
        return self.name

    def __call__(self):
        if self.args is None:
            self.func()
        else:
            self.func(*self.args)


def conn_matches_adapter(conn, adapter):
    setting_wireless = conn.get_setting_wireless()
    mac = setting_wireless.get_mac_address()
    if mac is not None:
        return mac == adapter.get_permanent_hw_address()

    setting_connection = conn.get_setting_connection()
    interface = setting_connection.get_interface_name()
    if interface is not None:
        return interface == adapter.get_iface()

    return True


def process_ap(nm_ap, is_active, adapter):
    if is_active:
        CLIENT.deactivate_connection_async(nm_ap, None, deactivate_cb, nm_ap)
        loop.run()
    else:
        conns_cur = [i for i in conns if
                     i.get_setting_wireless() is not None and
                     conn_matches_adapter(i, adapter)]
        con = nm_ap.filter_connections(conns_cur)
        if len(con) > 1:
            raise ValueError('There are multiple connections possible')

        if len(con) == 1:
            CLIENT.activate_connection_async(con[0], adapter, nm_ap.get_path(),
                                             None, activate_cb, nm_ap)
            loop.run()
        else:
            if ap_security(nm_ap) != '--':
                password = get_passphrase()
            else:
                password = ''
            set_new_connection(nm_ap, password, adapter)


def activate_cb(dev, res, data):
    try:
        conn = dev.activate_connection_finish(res)
    except GLib.Error:
        conn = None
    if conn is not None:
        notify(
            app=notify_app,
            summary='Network',
            body=f'Activated {conn.get_id()}',
            icon=notify_icon,
            urgent=1
        )
    else:
        notify(
            app=notify_app,
            summary='Network',
            body=f'Problem activating {data.get_id()}',
            icon=notify_icon,
            urgent=2
        )
    loop.quit()


def deactivate_cb(dev, res, data):
    if dev.deactivate_connection_finish(res) is True:
        notify(
            app=notify_app,
            summary='Network',
            body=f'Deactivated {data.get_id()}',
            icon=notify_icon,
            urgent=1
        )
    else:
        notify(
            app=notify_app,
            summary='Network',
            body=f'Problem deactivating {data.get_id()}',
            icon=notify_icon,
            urgent=2
        )
    loop.quit()


def process_vpngsm(con, activate):
    if activate:
        CLIENT.activate_connection_async(con, None, None,
                                         None, activate_cb, con)
    else:
        CLIENT.deactivate_connection_async(con, None, deactivate_cb, con)
    loop.run()


def create_ap_actions(aps, active_ap, active_connection, adapter):
    active_ap_bssid = active_ap.get_bssid() if active_ap is not None else ''

    names = [ssid_to_utf8(ap) for ap in aps]
    max_len_name = max([len(name) for name in names]) if names else 0
    secs = [ap_security(ap) for ap in aps]
    max_len_sec = max([len(sec) for sec in secs]) if secs else 0

    ap_actions = []

    for nm_ap, name, sec in zip(aps, names, secs):
        bars = NM.utils_wifi_strength_bars(nm_ap.get_strength())
        wifi_chars = network.get('wifi_chars', 'false')
        if wifi_chars:
            bars = ''.join([wifi_chars[i] for i, j in enumerate(bars) if j == '*'])
        is_active = nm_ap.get_bssid() == active_ap_bssid
        compact = network.get('compact', 'false')
        if compact:
            action_name = f'{name}  {sec}  {bars}'
        else:
            action_name = f'{name:<{max_len_name}s}  {sec:<{max_len_sec}s} {bars:>4}'
        if is_active:
            ap_actions.append(Action(action_name, process_ap,
                                     [active_connection, True, adapter],
                                     active=True))
        else:
            ap_actions.append(Action(action_name, process_ap,
                                     [nm_ap, False, adapter]))
    return ap_actions


def create_vpn_actions(vpns, active):
    active_vpns = [i for i in active if i.get_vpn()]
    return _create_vpngsm_actions(vpns, active_vpns, 'VPN')


def create_wireguard_actions(wgs, active):
    active_wgs = [i for i in active if i.get_connection_type() == 'wireguard']
    return _create_vpngsm_actions(wgs, active_wgs, 'Wireguard')


def create_eth_actions(eths, active):
    active_eths = [i for i in active if 'ethernet' in i.get_connection_type()]
    return _create_vpngsm_actions(eths, active_eths, 'Eth')


def create_gsm_actions(gsms, active):
    active_gsms = [i for i in active if
                   i.get_connection() is not None and
                   i.get_connection().is_type(NM.SETTING_GSM_SETTING_NAME)]
    return _create_vpngsm_actions(gsms, active_gsms, 'GSM')


def create_blue_actions(blues, active):
    active_blues = [i for i in active if
                    i.get_connection() is not None and
                    i.get_connection().is_type(NM.SETTING_BLUETOOTH_SETTING_NAME)]
    return _create_vpngsm_actions(blues, active_blues, 'Bluetooth')


def create_saved_actions(saved):
    return _create_vpngsm_actions(saved, [], "SAVED")


def _create_vpngsm_actions(cons, active_cons, label):
    active_con_ids = [a.get_id() for a in active_cons]
    actions = []
    for con in cons:
        is_active = con.get_id() in active_con_ids
        action_name = f'{con.get_id()}:{label}'
        if is_active:
            active_connection = [a for a in active_cons
                                 if a.get_id() == con.get_id()]
            if len(active_connection) != 1:
                raise ValueError(f'Multiple active connections match {con.get_id()}')
            active_connection = active_connection[0]

            actions.append(Action(action_name, process_vpngsm,
                                  [active_connection, False], active=True))
        else:
            actions.append(Action(action_name, process_vpngsm,
                                  [con, True]))
    return actions


def create_wwan_actions(client):
    wwan_enabled = client.wwan_get_enabled()
    wwan_action = 'Disable' if wwan_enabled else 'Enable'
    return [Action(f'{wwan_action} WWAN', toggle_wwan, not wwan_enabled)]


def combine_actions(eths, aps, vpns, wgs, gsms, blues, wwan, others, saved) -> list:
    compact = network.get('compact', 'false')
    empty_action = [Action('', None)] if not compact else []
    all_actions = []
    all_actions += eths + empty_action if eths else []
    all_actions += aps + empty_action if aps else []
    all_actions += vpns + empty_action if vpns else []
    all_actions += wgs + empty_action if wgs else []
    all_actions += gsms + empty_action if (gsms and wwan) else []
    all_actions += blues + empty_action if blues else []
    all_actions += wwan + empty_action if wwan else []
    all_actions += others + empty_action if others else []
    all_actions += saved + empty_action if saved else []
    return all_actions


def get_selection(all_actions):
    highlight = network.get('rofi_highlight', 'true')
    inp = []

    if highlight is True:
        inp = [str(action) for action in all_actions]
    else:
        inp = [('== ' if action.is_active else '   ') + str(action)
               for action in all_actions]
    active_lines = [index for index, action in enumerate(all_actions)
                    if action.is_active]

    match app:
        case 'rofi':
            sel = run(command(len(inp),
                              active_lines=active_lines,
                              config=passer(path_expander(conf))),
                      capture_output=True,
                      check=False,
                      input='\n'.join(inp),
                      encoding=enc,
                      env=env).stdout
        case 'wofi':
            sel = run(command(len(inp),
                              active_lines=active_lines,
                              config=path_expander(conf),
                              style=path_expander(style),
                              color=path_expander(color)),
                      capture_output=True,
                      check=False,
                      input='\n'.join(inp),
                      encoding=enc,
                      env=env).stdout
        case _:
            exit(1)

    if not sel.strip():
        exit(1)

    if highlight is False:
        action = [i for i in all_actions
                  if ((str(i).strip() == str(sel.strip())
                       and not i.is_active) or
                      ('== ' + str(i) == str(sel.rstrip())
                       and i.is_active))]
    else:
        action = [i for i in all_actions if str(i).strip() == sel.strip()]
    assert len(action) == 1, f'Selection was ambiguous: "{str(sel.strip())}"'
    return action[0]


def toggle_networking(enable):
    toggle = GLib.Variant.new_tuple(GLib.Variant.new_boolean(enable))
    try:
        CLIENT.dbus_call(NM.DBUS_PATH, NM.DBUS_INTERFACE, 'Enable', toggle,
                         None, -1, None, None, None)
    except AttributeError:
        CLIENT.networking_set_enabled(enable)
    notify(
        app=notify_app,
        summary='Network',
        body=f'Networking {"enabled" if enable is True else "disabled"}',
        icon=notify_icon,
        urgent=1
    )


def toggle_wifi(enable):
    toggle = GLib.Variant.new_boolean(enable)
    try:
        CLIENT.dbus_set_property(NM.DBUS_PATH, NM.DBUS_INTERFACE, 'WirelessEnabled', toggle,
                                 -1, None, None, None)
    except AttributeError:
        CLIENT.wireless_set_enabled(enable)
    notify(
        app=notify_app,
        summary='Wifi',
        body=f'Wifi {"enabled" if enable is True else "disabled"}',
        icon=notify_icon,
        urgent=1
    )


def toggle_wwan(enable):
    toggle = GLib.Variant.new_boolean(enable)
    try:
        CLIENT.dbus_set_property(NM.DBUS_PATH, NM.DBUS_INTERFACE, "WwanEnabled", toggle,
                                 -1, None, None, None)
    except AttributeError:
        CLIENT.wwan_set_enabled(enable)
    notify(
        app=notify_app,
        summary='Wwan',
        body=f'Wwan {"enabled" if enable is True else "disabled"}',
        icon=notify_icon,
        urgent=1
    )


def toggle_bluetooth(enable):
    type_bluetooth = 2
    op_change_all = 3
    idx = 0
    soft_state = 0 if enable else 1
    hard_state = 0

    data = pack("IBBBB", idx, type_bluetooth, op_change_all,
                soft_state, hard_state)

    try:
        with open('/dev/rfkill', 'r+b', buffering=0) as rff:
            rff.write(data)
    except PermissionError:
        notify(
            app=notify_app,
            summary='Lacking permission to write to /dev/rfkill.',
            body='Check networkmanager_dmenu github page for configuration options.',
            icon=notify_icon,
            urgent=3
        )
    else:
        notify(
            app=notify_app,
            summary='Bluetooth',
            body=f'Bluetooth {"enabled" if enable is True else "disabled"}',
            icon=notify_icon,
            urgent=2
        )


def launch_connection_editor():
    terminal = config.menu.get('terminal', 'alacritty')
    gui_if_available = network.get('gui_if_available', 'true')
    guis = ['gnome-control-center', 'nm-connection-editor']
    if gui_if_available is True:
        for gui in guis:
            if check_installed(gui):
                run(gui, check=False)
                return
    if check_installed('nmtui'):
        run([terminal, '-e', 'nmtui'], check=False)
        return
    notify(
        app=notify_app,
        summary='Network',
        body='No network connection editor installed',
        icon=notify_icon,
        urgent=2
    )


def get_passphrase():
    pinentry = network.get('pinentry', 'false')
    if pinentry:
        pin = ''
        out = run(pinentry,
                  capture_output=True,
                  check=False,
                  encoding=enc,
                  input='setdesc Get network password\ngetpin\n').stdout
        if out:
            res = out.rsplit()[2]
            if res.startswith('D '):
                pin = res.split('D ')[1]
        return pin

    match app:
        case 'rofi':
            sel = run(command(0,
                              promt='Passphrase',
                              config=passer(path_expander(conf))),
                      stdin=DEVNULL,
                      capture_output=True,
                      check=False,
                      encoding=enc).stdout
        case 'wofi':
            sel = run(command(0,
                              promt='Passphrase',
                              config=path_expander(conf),
                              style=path_expander(style),
                              color=path_expander(color)),
                      stdin=DEVNULL,
                      capture_output=True,
                      check=False,
                      encoding=enc).stdout
    return sel  # type: ignore


def delete_connection():
    conn_acts = [Action(i.get_id(), i.delete_async, args=[None, delete_cb, None]) for i in conns]
    conn_names = '\n'.join([str(i) for i in conn_acts])

    match app:
        case 'rofi':
            sel = run(command(len(conn_acts),
                              promt='Choose connection to delete: ',
                              config=passer(path_expander(conf))),
                      capture_output=True,
                      check=False,
                      input=conn_names,
                      encoding=enc,
                      env=env).stdout
        case 'wofi':
            sel = run(command(len(conn_acts),
                              promt='Choose connection to delete: ',
                              config=path_expander(conf),
                              style=path_expander(style),
                              color=path_expander(color)),
                      capture_output=True,
                      check=False,
                      input=conn_names,
                      encoding=enc,
                      env=env).stdout

    if not sel.rstrip():  # type: ignore
        exit(1)
    action = [i for i in conn_acts if str(i) == sel.rstrip()]  # type: ignore
    assert len(action) == 1, f'Selection was ambiguous: {str(sel)}'  # type: ignore
    action[0]()
    loop.run()


def delete_cb(dev, res, data):
    if dev.delete_finish(res) is True:
        notify(
            app=notify_app,
            summary='Connection',
            body=f'Deleted {dev.get_id()}',
            icon=notify_icon,
            urgent=1
        )
    else:
        notify(
            app=notify_app,
            summary='Connection',
            body=f'Problem deleting {dev.get_id()}',
            icon=notify_icon,
            urgent=2
        )
    loop.quit()


def set_new_connection(nm_ap, nm_pw, adapter):
    nm_pw = str(nm_pw).strip()
    profile = create_wifi_profile(nm_ap, nm_pw, adapter)
    CLIENT.add_and_activate_connection_async(profile, adapter, nm_ap.get_path(),
                                             None, verify_conn, profile)
    loop.run()


def create_wifi_profile(nm_ap, password, adapter):
    ap_sec = ap_security(nm_ap)
    profile = NM.SimpleConnection.new()

    s_con = NM.SettingConnection.new()
    s_con.set_property(NM.SETTING_CONNECTION_ID, ssid_to_utf8(nm_ap))
    s_con.set_property(NM.SETTING_CONNECTION_UUID, str(uuid4()))
    s_con.set_property(NM.SETTING_CONNECTION_TYPE, '802-11-wireless')
    profile.add_setting(s_con)

    s_wifi = NM.SettingWireless.new()
    s_wifi.set_property(NM.SETTING_WIRELESS_SSID, nm_ap.get_ssid())
    s_wifi.set_property(NM.SETTING_WIRELESS_MODE, 'infrastructure')
    s_wifi.set_property(NM.SETTING_WIRELESS_MAC_ADDRESS, adapter.get_permanent_hw_address())
    profile.add_setting(s_wifi)

    s_ip4 = NM.SettingIP4Config.new()
    s_ip4.set_property(NM.SETTING_IP_CONFIG_METHOD, 'auto')
    profile.add_setting(s_ip4)

    s_ip6 = NM.SettingIP6Config.new()
    s_ip6.set_property(NM.SETTING_IP_CONFIG_METHOD, 'auto')
    profile.add_setting(s_ip6)

    if ap_sec != '--':
        s_wifi_sec = NM.SettingWirelessSecurity.new()
        if 'WPA' in ap_sec:
            if 'WPA3' in ap_sec:
                s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT,
                                        'sae')
            else:
                s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT,
                                        'wpa-psk')
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_AUTH_ALG,
                                    'open')
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_PSK, password)
        elif 'WEP' in ap_sec:
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_KEY_MGMT,
                                    'None')
            s_wifi_sec.set_property(NM.SETTING_WIRELESS_SECURITY_WEP_KEY_TYPE,
                                    NM.WepKeyType.PASSPHRASE)
            s_wifi_sec.set_wep_key(0, password)
        profile.add_setting(s_wifi_sec)

    return profile


def verify_conn(client, result, data):
    try:
        act_conn = client.add_and_activate_connection_finish(result)
        conn = act_conn.get_connection()
        if not all([conn.verify(),
                    conn.verify_secrets(),
                    data.verify(),
                    data.verify_secrets()]):
            raise GLib.Error
        notify(
            app=notify_app,
            summary='Connection',
            body=f'Added {conn.get_id()}',
            icon=notify_icon,
            urgent=1
        )
    except GLib.Error:
        try:
            notify(
                app=notify_app,
                summary='Connection',
                body=f'Connection to {conn.get_id()} failed',  # type: ignore
                icon=notify_icon,
                urgent=2
            )
            conn.delete_async(None, None, None)  # type: ignore
        except UnboundLocalError:
            pass
    finally:
        loop.quit()


def create_ap_list(adapter, active_connections):
    aps = []
    ap_names = []
    active_ap = adapter.get_active_access_point()
    aps_all = sorted(adapter.get_access_points(),
                     key=lambda a: a.get_strength(), reverse=True)
    conns_cur = [i for i in conns if
                 i.get_setting_wireless() is not None and
                 conn_matches_adapter(i, adapter)]
    try:
        ap_conns = active_ap.filter_connections(conns_cur)
        active_ap_name = ssid_to_utf8(active_ap)
        active_ap_con = [active_conn for active_conn in active_connections
                         if active_conn.get_connection() in ap_conns]
    except AttributeError:
        active_ap_name = None
        active_ap_con = []
    if len(active_ap_con) > 1:
        raise ValueError('Multiple connection profiles match'
                         ' the wireless AP')
    active_ap_con = active_ap_con[0] if active_ap_con else None
    for nm_ap in aps_all:
        ap_name = ssid_to_utf8(nm_ap)
        if nm_ap != active_ap and ap_name == active_ap_name:
            continue
        if ap_name not in ap_names:
            ap_names.append(ap_name)
            aps.append(nm_ap)
    return aps, active_ap, active_ap_con, adapter


def main():
    active = CLIENT.get_active_connections()
    adapter = choose_adapter(CLIENT)
    if adapter:
        ap_actions = create_ap_actions(*create_ap_list(adapter, active))
    else:
        ap_actions = []

    vpns = [i for i in conns if i.is_type(NM.SETTING_VPN_SETTING_NAME)]
    try:
        wgs = [i for i in conns if i.is_type(NM.SETTING_WIREGUARD_SETTING_NAME)]
    except AttributeError:
        wgs = []
    eths = [i for i in conns if i.is_type(NM.SETTING_WIRED_SETTING_NAME)]
    blues = [i for i in conns if i.is_type(NM.SETTING_BLUETOOTH_SETTING_NAME)]

    vpn_actions = create_vpn_actions(vpns, active)
    wg_actions = create_wireguard_actions(wgs, active)
    eth_actions = create_eth_actions(eths, active)
    blue_actions = create_blue_actions(blues, active)
    other_actions = create_other_actions(CLIENT)
    wwan_installed = check_installed('ModemManager')
    if wwan_installed:
        gsms = [i for i in conns if i.is_type(NM.SETTING_GSM_SETTING_NAME)]
        gsm_actions = create_gsm_actions(gsms, active)
        wwan_actions = create_wwan_actions(CLIENT)
    else:
        gsm_actions = []
        wwan_actions = []

    list_saved = network.get('list_saved', 'true')
    saved_cons = [i for i in conns if i not in vpns + wgs + eths + blues]
    if list_saved:
        saved_actions = create_saved_actions(saved_cons)
    else:
        saved_actions = [Action('Saved connections', prompt_saved, [saved_cons])]

    actions = combine_actions(eth_actions, ap_actions, vpn_actions, wg_actions,
                              gsm_actions, blue_actions, wwan_actions,
                              other_actions, saved_actions)
    sel = get_selection(actions)
    sel()


if __name__ == '__main__':
    term, network = (
        config.menu.terminal,
        config.menu.network,
    )
    app = config.menu.get('app', 'rofi')
    conf, style, color = (
        network.config,
        network.style,
        network.colors
    )
    env, enc = (
        environ.copy(),
        getpreferredencoding()
    )
    notify_app, notify_icon = (
        'Network Manager',
        '/usr/share/icons/Adwaita/scalable/devices/network-wired-symbolic.svg'
    )

    CLIENT = NM.Client.new(None)
    loop = GLib.MainLoop()
    conns = CLIENT.get_connections()
    cmd = split(app)
    env['LC_ALL'] = 'C'

    main()
