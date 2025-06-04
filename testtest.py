from ultralytics import YOLO

# Load a pretrained YOLO11n model
model = YOLO(r"C:\Users\32928\PycharmProjects\myweb\best.pt")

# Define path to the image file
source = r"C:\Users\32928\PycharmProjects\myweb\uploads\100_1_original.png"

# Run inference on the source
results = model(source,save=True)  # list of Results objects
for r in results:
    print(r.boxes.xyxy)
    print(r.boxes.cls)
USE demo01;

CREATE TABLE 'login_user'(

  'id' INT NOT NULL AUTO_INCREMENT,

  'username' VARCHAR(45) NOT NULL,

  'password' VARCHAR(45) NOT NULL,

  PRIMARY KEY ('id'),

  UNIQUE INDEX 'idlogin_user_UNIQUE' ('id' ASC),

  UNIQUE INDEX 'username_UNIQUE' ('username' ASC)) ;