/*
 * BMduino-UNO 安全警示車控制韌體
 * 適用於 HT32F52367 (BM53A367A)
 * 
 * 功能：
 * - 透過序列埠接收指令控制馬達、伺服、警報、LED
 * - 讀取光感測值並自動調整 LED 亮度
 * 
 * 通訊協定（115200 baud）：
 * - M F <speed>  : 馬達前進，速度 0-100
 * - M B <speed>  : 馬達後退，速度 0-100
 * - M S 0        : 馬達停止
 * - S U          : 伺服升起警示牌
 * - S D          : 伺服放下警示牌
 * - A P <secs>   : 播放警報（秒數）
 * - L S <value>  : 設定 LED 亮度 0-255
 * - Q L          : 查詢光感測值（回傳 "L <value>"）
 */

// ===== 腳位定義（根據 BM53A367A 手冊，Arduino UNO 相容腳位）=====

// L298N 馬達驅動（左馬達）
#define MOTOR_LEFT_IN1  5   // D5 (PWM)
#define MOTOR_LEFT_IN2  6   // D6 (PWM)
#define MOTOR_LEFT_ENA  9   // D9 (PWM)

// L298N 馬達驅動（右馬達）
#define MOTOR_RIGHT_IN3 10  // D10 (PWM)
#define MOTOR_RIGHT_IN4 11  // D11 (PWM)
#define MOTOR_RIGHT_ENB  3  // D3 (PWM)

// 伺服馬達（360度伺服，使用 PWM）
#define SERVO_1_PIN     4   // D4 (PWM)
#define SERVO_2_PIN     7   // D7 (PWM)

// ISD1820 警報模組
#define ALARM_PIN       8   // D8

// LED 燈條（透過 MOSFET 控制）
#define LED_PIN         12  // D12 (PWM)

// 光感測模組（類比輸入）
#define LIGHT_SENSOR_PIN A0 // A0

// ===== 全域變數 =====
String inputString = "";      // 接收序列埠字串
boolean stringComplete = false; // 是否收到完整指令

// 伺服角度設定
int servo1_angle = 0;  // 0-180
int servo2_angle = 0;  // 0-180

// LED 自動亮度控制
unsigned long lastLightRead = 0;
const unsigned long LIGHT_READ_INTERVAL = 100; // 每 100ms 讀取一次光感測
bool autoBrightness = false; // 是否啟用自動亮度

// ===== 設定 =====
void setup() {
  // 初始化序列埠
  Serial.begin(115200);
  Serial.setTimeout(100);
  
  // 等待序列埠就緒
  delay(1000);
  
  // 設定馬達腳位為輸出
  pinMode(MOTOR_LEFT_IN1, OUTPUT);
  pinMode(MOTOR_LEFT_IN2, OUTPUT);
  pinMode(MOTOR_LEFT_ENA, OUTPUT);
  pinMode(MOTOR_RIGHT_IN3, OUTPUT);
  pinMode(MOTOR_RIGHT_IN4, OUTPUT);
  pinMode(MOTOR_RIGHT_ENB, OUTPUT);
  
  // 設定伺服腳位為輸出（PWM）
  pinMode(SERVO_1_PIN, OUTPUT);
  pinMode(SERVO_2_PIN, OUTPUT);
  
  // 設定警報腳位為輸出
  pinMode(ALARM_PIN, OUTPUT);
  digitalWrite(ALARM_PIN, LOW);
  
  // 設定 LED 腳位為輸出（PWM）
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);
  
  // 設定光感測為輸入
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  
  // 初始化馬達為停止狀態
  stopMotor();
  
  // 初始化伺服為降下狀態
  setServoAngle(1, 0);
  setServoAngle(2, 0);
  
  // 準備接收序列埠指令
  inputString.reserve(32);
  
  Serial.println("BMduino Ready");
  Serial.println("Commands: M F/B/S <speed>, S U/D, A P <secs>, L S <value>, Q L");
}

// ===== 主迴圈 =====
void loop() {
  // 處理序列埠指令
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // 自動讀取光感測並調整 LED 亮度（如果啟用）
  if (autoBrightness) {
    unsigned long now = millis();
    if (now - lastLightRead >= LIGHT_READ_INTERVAL) {
      adjustLEDByLight();
      lastLightRead = now;
    }
  }
  
  delay(10);
}

// ===== 序列埠接收 =====
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else if (inChar != '\r') {
      inputString += inChar;
    }
  }
}

// ===== 指令處理 =====
void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  
  if (cmd.length() == 0) return;
  
  // 解析指令
  int space1 = cmd.indexOf(' ');
  int space2 = cmd.indexOf(' ', space1 + 1);
  
  String cmdType = cmd.substring(0, space1 > 0 ? space1 : cmd.length());
  String param1 = space1 > 0 ? cmd.substring(space1 + 1, space2 > 0 ? space2 : cmd.length()) : "";
  String param2 = space2 > 0 ? cmd.substring(space2 + 1) : "";
  
  // 馬達控制: M F/B/S <speed>
  if (cmdType == "M") {
    if (param1 == "F") {
      int speed = param2.toInt();
      setMotor('F', speed);
    } else if (param1 == "B") {
      int speed = param2.toInt();
      setMotor('B', speed);
    } else if (param1 == "S") {
      stopMotor();
    }
  }
  // 伺服控制: S U/D
  else if (cmdType == "S") {
    if (param1 == "U") {
      raiseSign();
    } else if (param1 == "D") {
      lowerSign();
    }
  }
  // 警報控制: A P <secs>
  else if (cmdType == "A") {
    if (param1 == "P") {
      int duration = param2.toInt();
      playAlarm(duration);
    }
  }
  // LED 控制: L S <value>
  else if (cmdType == "L") {
    if (param1 == "S") {
      int brightness = param2.toInt();
      setLEDBrightness(brightness);
      autoBrightness = false; // 手動設定時關閉自動亮度
    }
  }
  // 查詢光感測: Q L
  else if (cmdType == "Q") {
    if (param1 == "L") {
      int lightValue = analogRead(LIGHT_SENSOR_PIN);
      Serial.print("L ");
      Serial.println(lightValue);
    }
  }
}

// ===== 馬達控制 =====
void setMotor(char direction, int speed) {
  speed = constrain(speed, 0, 100);
  int pwmValue = map(speed, 0, 100, 0, 255);
  
  if (direction == 'F') {
    // 前進
    digitalWrite(MOTOR_LEFT_IN1, HIGH);
    digitalWrite(MOTOR_LEFT_IN2, LOW);
    digitalWrite(MOTOR_RIGHT_IN3, HIGH);
    digitalWrite(MOTOR_RIGHT_IN4, LOW);
    analogWrite(MOTOR_LEFT_ENA, pwmValue);
    analogWrite(MOTOR_RIGHT_ENB, pwmValue);
  } else if (direction == 'B') {
    // 後退
    digitalWrite(MOTOR_LEFT_IN1, LOW);
    digitalWrite(MOTOR_LEFT_IN2, HIGH);
    digitalWrite(MOTOR_RIGHT_IN3, LOW);
    digitalWrite(MOTOR_RIGHT_IN4, HIGH);
    analogWrite(MOTOR_LEFT_ENA, pwmValue);
    analogWrite(MOTOR_RIGHT_ENB, pwmValue);
  }
}

void stopMotor() {
  digitalWrite(MOTOR_LEFT_IN1, LOW);
  digitalWrite(MOTOR_LEFT_IN2, LOW);
  digitalWrite(MOTOR_RIGHT_IN3, LOW);
  digitalWrite(MOTOR_RIGHT_IN4, LOW);
  analogWrite(MOTOR_LEFT_ENA, 0);
  analogWrite(MOTOR_RIGHT_ENB, 0);
}

// ===== 伺服控制 =====
void setServoAngle(int servoNum, int angle) {
  angle = constrain(angle, 0, 180);
  
  // 計算 PWM duty cycle（50Hz，0度=2.5%，180度=12.5%）
  // 對於 Arduino，使用 analogWrite 模擬 PWM（但頻率可能不是 50Hz）
  // 建議使用 Servo 函式庫，這裡使用簡化版本
  
  int pin = (servoNum == 1) ? SERVO_1_PIN : SERVO_2_PIN;
  
  // 簡化版本：使用 analogWrite（實際應用建議使用 Servo 函式庫）
  // 注意：這只是近似，實際應使用正確的 50Hz PWM
  int pwmValue = map(angle, 0, 180, 25, 125); // 約 2.5% 到 12.5% 的 duty cycle
  analogWrite(pin, pwmValue);
  
  if (servoNum == 1) {
    servo1_angle = angle;
  } else {
    servo2_angle = angle;
  }
  
  delay(300); // 等待伺服轉動
}

void raiseSign() {
  setServoAngle(1, 90);  // 升起角度
  setServoAngle(2, 90);
}

void lowerSign() {
  setServoAngle(1, 0);   // 降下角度
  setServoAngle(2, 0);
}

// ===== 警報控制 =====
void playAlarm(int duration) {
  duration = constrain(duration, 1, 10); // 限制 1-10 秒
  
  // ISD1820 觸發播放：將 PLAY 腳位拉高
  digitalWrite(ALARM_PIN, HIGH);
  delay(duration * 1000);
  digitalWrite(ALARM_PIN, LOW);
}

// ===== LED 控制 =====
void setLEDBrightness(int brightness) {
  brightness = constrain(brightness, 0, 255);
  analogWrite(LED_PIN, brightness);
}

// ===== 光感測自動亮度 =====
void adjustLEDByLight() {
  int lightValue = analogRead(LIGHT_SENSOR_PIN);
  
  // 映射光感測值到 LED 亮度（越暗越亮）
  // 假設光感測值範圍 0-1023（10-bit ADC）
  int brightness = map(lightValue, 0, 1023, 255, 0); // 反向映射
  brightness = constrain(brightness, 0, 255);
  
  analogWrite(LED_PIN, brightness);
}

