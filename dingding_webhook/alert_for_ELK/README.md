用于监测ELK中JAVA日志告警
```

```
1. 查询非INFO的日志  hostname，tag，local_time
1. lostname_tag 作为唯一名 local_time 和 loglevel作为属性
1. 告警策略，收到ERROR且数据库中不存在该ERROR或时间
