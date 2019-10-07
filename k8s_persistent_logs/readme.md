# 基于elk的k8s日志持久化
通过elk采集k8s日志后，为适应不同开发人员对日志的需求，对日志进行持久化

## 逻辑
每个服务部署为deployment，并打上唯一label`app=$APP_NAME`

脚本通过查询k8s APIserver获取所有deployment，通过deployment获取label app，并以此为关键字检索es，查询该应用日志，并持久化为日志文件

目前的颗粒度为deployment，后期会改为pod，并通过多线程实现