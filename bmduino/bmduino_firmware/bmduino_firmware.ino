/*
 * BMduino-UNO 安全警示車控制韌體
 * 適用於 HT32F52367 (BM53A367A)
 * 
 * 功能：
 * - 透過序列埠接收指令控制馬達、伺服、警報、LED
 * 
 * 通訊協定（9600 baud，UART 硬體序列埠）：
 * - M F <speed>  : 馬達前進，速度 0-100
 * - M B <speed>  : 馬達後退，速度 0-100
 * - M S 0        : 馬達停止
 * - S U          : 伺服升起警示牌
 * - S D          : 伺服放下警示牌
 * - A P <secs>   : 播放警報（秒數）
 * - L S <value>  : 設定 LED 亮度 0-255
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

// 伺服馬達（標準 180度伺服，如 MG90S，使用 50Hz PWM）
#define SERVO_1_PIN     4   // D4
#define SERVO_2_PIN     7   // D7

// ISD1820 警報模組
#define ALARM_PIN       8   // D8

// LED 燈條（透過 MOSFET 控制）
#define LED_PIN         12  // D12 (PWM)

// ===== 全域變數 =====
String inputString = "";      // 接收序列埠字串
boolean stringComplete = false; // 是否收到完整指令

// 伺服角度設定
int servo1_angle = 0;  // 0-180
int servo2_angle = 0;  // 0-180

// PWM 控制變數
unsigned long lastServoUpdate = 0;
const unsigned long SERVO_PULSE_INTERVAL = 20; // 50Hz = 20ms 週期

// ===== 設定 =====
void setup() {
  // 初始化序列埠（UART 硬體序列埠，9600 baud）
  Serial.begin(9600);
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
  
  // 設定伺服腳位為輸出
  pinMode(SERVO_1_PIN, OUTPUT);
  pinMode(SERVO_2_PIN, OUTPUT);
  digitalWrite(SERVO_1_PIN, LOW);
  digitalWrite(SERVO_2_PIN, LOW);
  
  // 設定警報腳位為輸出
  pinMode(ALARM_PIN, OUTPUT);
  digitalWrite(ALARM_PIN, LOW);
  
  // 設定 LED 腳位為輸出（PWM）
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);
  
  // 初始化馬達為停止狀態
  stopMotor();
  
  // 初始化伺服為降下狀態
  setServoAngle(1, 0);
  setServoAngle(2, 0);
  
  // 準備接收序列埠指令
  inputString.reserve(32);
  
  Serial.println("BMduino Ready");
  Serial.println("Commands: M F/B/S <speed>, S U/D, A P <secs>, L S <value>");
}

// ===== 主迴圈 =====
void loop() {
  // 處理序列埠指令
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // 持續產生伺服 PWM 訊號（50Hz，每 20ms 一次）
  unsigned long now = millis();
  if (now - lastServoUpdate >= SERVO_PULSE_INTERVAL) {
    updateServoPWM();
    lastServoUpdate = now;
  }
  
  delay(1); // 減少延遲，讓 PWM 更穩定
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
// MG90S 標準伺服控制規格：
// - 50Hz PWM（20ms 週期）
// - 0.5ms 脈衝 = 0 度
// - 1.5ms 脈衝 = 90 度
// - 2.5ms 脈衝 = 180 度

void setServoAngle(int servoNum, int angle) {
  angle = constrain(angle, 0, 180);
  
  if (servoNum == 1) {
    servo1_angle = angle;
  } else if (servoNum == 2) {
    servo2_angle = angle;
  }
}

// 更新伺服 PWM 訊號（在 loop() 中每 20ms 呼叫一次）
void updateServoPWM() {
  // 計算脈衝寬度（微秒）
  // 角度 0-180 對應脈衝 500-2500 微秒
  int pulse1 = map(servo1_angle, 0, 180, 500, 2500);
  int pulse2 = map(servo2_angle, 0, 180, 500, 2500);
  
  // 產生 PWM 脈衝
  // 伺服 1
  digitalWrite(SERVO_1_PIN, HIGH);
  delayMicroseconds(pulse1);
  digitalWrite(SERVO_1_PIN, LOW);
  
  // 伺服 2
  digitalWrite(SERVO_2_PIN, HIGH);
  delayMicroseconds(pulse2);
  digitalWrite(SERVO_2_PIN, LOW);
  
  // 剩餘時間保持 LOW（總週期 20ms）
  // 注意：如果兩個脈衝總時間超過 20ms，需要調整
  unsigned long totalPulse = pulse1 + pulse2;
  if (totalPulse < 20000) {
    delayMicroseconds(20000 - totalPulse);
  }
}

void raiseSign() {
  setServoAngle(1, 90);  // 升起角度（90度）
  setServoAngle(2, 90);
  // 等待伺服轉動（PWM 會在 loop() 中持續產生）
  delay(500);
}

void lowerSign() {
  setServoAngle(1, 0);   // 降下角度（0度）
  setServoAngle(2, 0);
  // 等待伺服轉動（PWM 會在 loop() 中持續產生）
  delay(500);
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

