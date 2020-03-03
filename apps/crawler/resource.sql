CREATE TABLE `resource` (
  `name` varchar(20) NOT NULL COMMENT '英文名, 唯一标识',
  `cn_name` varchar(20) DEFAULT NULL COMMENT '中文名',
  `config` text COMMENT '资源配置',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '接入时间',
  `contact` varchar(20) DEFAULT NULL COMMENT '联系人',
  `desc` text COMMENT '资源描述',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8