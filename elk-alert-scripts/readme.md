elk告警脚本，dsl里通过字典形式存储钉钉webhook API(类型list)，还有相应的DSL查询语句

循环list内多个webhook解决钉钉API每分钟二十次限制

脚本需要crontab设置为每分钟一次