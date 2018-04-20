# 监测ELK中JAVA日志等级并告警
实现监控ELK中JAVA日志并推送所有非INFO信息，推送通过钉钉实现
## 模块
分两个模块：
* 查询告警模块
* 告警恢复模块

## 查询告警模块
* 查询非INFO的日志，对比数据库中该项目的trigger状态
* 若为trigger则刷新trigger时间
* 若为resolved则发出告警并记录告警的相关参数
* 告警消息通过钉钉机器人推送

## 告警恢复模块
* 遍历数据库中trigger状态
* 若距离上一次trigger刷新时间大于一定时间间隔，则发出恢复信息

## 相关设计
### 告警数据
告警数据以json格式存储在elasticsearch中，`_index=wyny_elk`,`_type=alert`,`_id={hostname}_{tags}`,详细格式如下：
```json
PUT /wyny_elk/alert/hadoop1_namenode_loglevel
{
  "log_time":"2018-04-15 03:32:42 123",
  "trigger_status":"alert"
}
```
查看elasticsearch告警信息:
```json
GET /wyny_elk/alert/hadoop1_namenode_loglevel

{
  "_index": "wyny_elk",
  "_type": "alert",
  "_id": "hadoop1_namenode",
  "_version": 1,
  "found": true,
  "_source": {
    "log_time": "2018-04-15 03:32:42 123",
    "trigger_status": "alert"
  }
}
```
### 告警消息推送
推送至钉钉自定机器人，格式为markdown
```json
webhook_message = {
"msgtype": "markdown",
"markdown": {
    "title":"markdown测试",
    "text":{
# 状态： {log_level}告警
**主机名：** {hostname}
**告警模块：** {tag}
**日志时间：** {log_time}
**日志等级：** {log_level}
**日志内容：** {log_message}
}
}
}
```

