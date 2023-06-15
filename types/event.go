package types

import "time"

type NodeEvent struct {
	Id       string
	Name     string
	DateTime time.Time
	Type     NodeStatusType
}
