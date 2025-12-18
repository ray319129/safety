"""
BMduino 控制模組
透過序列埠與 BMduino-UNO 通訊，控制馬達、伺服、警報與 LED。
"""

import time
from typing import Optional

import serial


class BMduinoController:
    """BMduino 控制類別

    通訊協定（建議）：純文字、一行一指令，以 `\\n` 結尾，例如：
    - `M F 60`  : 馬達前進、速度 60
    - `M B 40`  : 馬達後退、速度 40
    - `M S 0`   : 馬達停止
    - `S U`     : 伺服升起警示牌 (Sign Up)
    - `S D`     : 伺服放下警示牌 (Sign Down)
    - `A P 3`   : 播放警報 3 秒
    - `L S 128` : 設定 LED 亮度 0–255
    """

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

        self.connect()

    def connect(self) -> None:
        """建立與 BMduino 的序列連線。"""
        if self.ser and self.ser.is_open:
            return

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            # 給 BMduino 一點時間重置
            time.sleep(2.0)
            print(f"已連線至 BMduino: {self.port} @ {self.baudrate}")
        except Exception as e:
            print(f"無法連線至 BMduino ({self.port}): {e}")
            self.ser = None

    def _send_command(self, cmd: str, expect_response: bool = False) -> Optional[str]:
        """送出指令至 BMduino。

        Args:
            cmd: 不含換行的指令字串
            expect_response: 是否預期有一行回應
        Returns:
            回應字串（去除換行），或 None
        """
        if not self.ser or not self.ser.is_open:
            self.connect()
            if not self.ser:
                return None

        try:
            line = (cmd.strip() + "\n").encode("utf-8")
            self.ser.write(line)
            self.ser.flush()

            if expect_response:
                resp = self.ser.readline().decode("utf-8", errors="ignore").strip()
                return resp
        except Exception as e:
            print(f"BMduino 指令失敗 ({cmd}): {e}")
        return None

    # ===== 高階控制方法 =====
    def set_motor(self, direction: str, speed: int) -> None:
        """設定馬達動作。

        direction: 'F' 前進, 'B' 後退, 'S' 停止
        speed: 0–100
        """
        direction = direction.upper()
        speed = max(0, min(100, int(speed)))
        if direction not in ("F", "B", "S"):
            direction = "S"
        self._send_command(f"M {direction} {speed}")

    def stop_motor(self) -> None:
        """停止馬達。"""
        self.set_motor("S", 0)

    def raise_sign(self) -> None:
        """升起警示牌。"""
        self._send_command("S U")

    def lower_sign(self) -> None:
        """放下警示牌。"""
        self._send_command("S D")

    def play_alarm(self, duration: float = 3.0) -> None:
        """播放警報。

        Args:
            duration: 播放秒數（BMduino 端可決定是否精準使用此參數）
        """
        secs = max(1, int(round(duration)))
        self._send_command(f"A P {secs}")

    def set_led_brightness(self, value: int) -> None:
        """設定 LED 亮度 (0–255)。"""
        value = max(0, min(255, int(value)))
        self._send_command(f"L S {value}")

    def close(self) -> None:
        """關閉序列連線。"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None


__all__ = ["BMduinoController"]