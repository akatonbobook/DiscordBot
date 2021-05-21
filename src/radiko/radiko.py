import base64
import datetime
import enum
import time
import xml.etree.ElementTree as ET

import m3u8
import requests


class AuthError(Exception):
    """認証失敗を知らせる例外クラス
    """
    pass


class CannotGetError(Exception):
    """HTTPリクエストに失敗したことを知らせる例外クラス
    """
    pass


class NotSelectedError(Exception):
    """局が選択されていないことを知らせる例外クラス
    """
    pass


_authKey = b'bcd151073c03b352e1ef2fd66c32209da9ca0afa'

_URL_AUTH1 = 'https://radiko.jp/v2/api/auth1'
_URL_AUTH2 = 'https://radiko.jp/v2/api/auth2'
_URL_PROGRAM = 'https://radiko.jp/v3/program/date/{date}/{area}.xml'
_URL_GET_LIST = 'http://f-radiko.smartstream.ne.jp/{st}/_definst_/' \
                + 'simul-stream.stream/playlist.m3u8'


def _get_partial_key(r):
    offset = int(r.headers["X-Radiko-KeyOffset"])
    length = int(r.headers["X-Radiko-KeyLength"])
    return base64.b64encode(_authKey[offset: offset + length])


def _get_date(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    if dt.hour < 5:
        dt -= datetime.timedelta(days=1)
    return dt.strftime("%Y%m%d")


class ProgState(enum.IntEnum):
    before = enum.auto()
    onair = enum.auto()
    after = enum.auto()


class Radiko:
    """RadikoAPIにアクセスするためのクライアントクラス
    """

    def __init__(self):
        """
        
        Raise:
            AuthError:　認証に失敗した場合に発生
        """
        self.area = None
        self.headers = {
            'x-radiko-app': 'pc_html5',
            'x-radiko-app-version': '0.0.1',
            'x-radiko-user': 'dummy_user',
            'x-radiko-device': 'pc',
            'x-radiko-authtoken': '',
            'x-radiko-partialkey': ''
        }
        self.stations = []
        self.select = None

        self.get_auth()
        
        self.get_info()
        self.select_station(0)

    def get_auth(self):
        """認証を取得する関数

        RadikoApiにアクセスして認証を取得する．
        """
        r = requests.get(_URL_AUTH1, headers=self.headers)
        if r.status_code != 200:
            raise AuthError("認証1に失敗")
        self.headers["x-radiko-authtoken"] = r.headers["X-RADIKO-AUTHTOKEN"]
        self.headers["x-radiko-partialkey"] = _get_partial_key(r)

        r = requests.get(_URL_AUTH2, headers=self.headers)
        if r.status_code != 200:
            raise AuthError("認証2に失敗")
        self.area = r.content.decode().split(',')[0]

    def get_info(self, dt=None, remove=False, removepast=True):
        """受信できる局，番組を取得する関数
            
        指定した日時の情報を取得する．
        指定しない場合は現在の情報を取得する．

        Args:
            dt (datetime): 日時

        Raises:
            CannotGetError: リクエストに失敗した場合に発生

        Returns:
            List: 受信可能な局のリスト
        """
        
        self.get_auth()

        r = requests.get(_URL_PROGRAM.format(date=_get_date(dt), area=self.area),
                headers=self.headers)
        if r.status_code != 200:
            raise CannotGetError("取得に失敗しました")
        x_program = ET.fromstring(r.content.decode())
        x_stations = x_program.find("stations").findall("station")
        for x_station in x_stations:
            new_station = Station(x_station)
            for station in self.stations:
                if station.id == new_station.id:
                    station._load_programs(x_station)
                    break
                if remove:
                    station._remove_programs(dt)
                if removepast:
                    station._remove_programs()
            else:
                self.stations.append(new_station)

            
        return self.stations[:]
    
    def get_stream(self, identifier=None):
        """放送のストリームURLを取得する関数

        identifierを指定しない場合はすでに選択されている局のストリームを返す

        Args:
            identifier (:obj:str, optional): 局のidまたはidxまたは名前
        
        Raises:
            NotSelectedError: 局が選択されていない場合に発生
            CannotGetError: リクエストに失敗した場合に発生

        Returns:
            str: ストリームURL
        """
        
        self.get_auth()

        if identifier != None:
            self.select_station(identifier)

        if self.select == None:
            raise NotSelectedError("局が選択されていません")

        r = requests.get(_URL_GET_LIST.format(st=self.select.id), headers=self.headers)
        if r.status_code != 200:
            raise CannotGetError("取得に失敗しました")
        m3u8_obj = m3u8.loads(r.content.decode())
        return m3u8_obj.playlists[0].uri

    def select_station(self, identifier=None):
        """局を選択する関数

        Args:
            identifier (str): 局のidまたはidxまたは名前
        
        Returns:
            Station: 現在選択されている局
        """
        if type(identifier) == str:
            if identifier.isdecimal():
                identifier = int(identifier)

        if type(identifier) == int:
            idx = identifier
            if 0 <= idx < len(self.stations):
                self.select = self.stations[idx]
                return self.select
        elif type(identifier) == Station:
            self.select == identifier
            return
        elif type(identifier) == str:
            for station in self.stations:
                if identifier == station.id:
                    self.select = station
                    return
                elif identifier == station.name:
                    self.select = station
                    return self.select
        return self.select


class Station:
    """局を表すクラス
    """

    def __init__(self, x_station):
        self.progs = []
        self.id = x_station.attrib["id"]
        self.name = x_station.find("name").text
        self._load_programs(x_station)

    def _load_programs(self, x_station):
        x_progs = x_station.find("progs")
        for x_prog in x_progs.findall("prog"):
            new_p = Prog(x_prog)
            for prog in self.progs:
                if prog.id == new_p.id:
                    break
            else:
                self.progs.append(new_p)
        self.progs.sort(key=lambda p: p.ft)

    def _remove_programs(self, dt=None):
        if dt == None:
            dt = datetime.datetime.now()
        self.progs.sort(key=lambda p: p.ft)
        while True:
            if len(self.progs) == 0:
                break
            if self.progs[0].get_state(dt) == ProgState.after:
                self.progs.pop(0)
                continue
            else:
                break

    def get_on_air(self, dt=None):
        """放送中の番組を返す関数

        指定したdatetimeで放送中の番組を返す.
        指定しない場合は現在時刻が指定される.

        Args:
            dt (datetime): 日時

        Return:
            Prog: 放送中の番組

        Note:
            翌日の動作について保証しない
        """

        if dt is None:
            dt = datetime.datetime.now()

        for prg in self.progs:
            if prg.get_state(dt) == ProgState.onair:
                return prg
        else:
            return None


class Prog:
    """番組を表すクラス
    """

    def __init__(self, x_prg):
        self.id = x_prg.attrib["id"]
        self.master_id = x_prg.attrib["master_id"]
        self.ft = datetime.datetime.strptime(x_prg.attrib["ft"][0:12], "%Y%m%d%H%M")
        self.to = datetime.datetime.strptime(x_prg.attrib["to"][0:12], "%Y%m%d%H%M")
        self.title = x_prg.find("title").text
        self.url = x_prg.find("url").text
        self.pfm = x_prg.find("pfm").text
        self.img = x_prg.find("img").text

    def get_state(self, dt=None):
        """番組の状態を返す関数

        指定した時刻での番組の状態を返す．
        時刻を指定しない場合，現在時刻での状態を返す．

        Args:
            dt (datetime): 時刻
        
        Returns:
            ProgState: 番組の状態
        """
        if dt == None:
            dt = datetime.datetime.now()

        if dt < self.ft:
            return ProgState.before
        elif self.ft <= dt < self.to:
            return ProgState.onair
        else:
            return ProgState.after


if __name__ == "__main__":
    client = Radiko()
    print(str(len(client.stations[0].progs)))
