package types

import "time"

type NodeEvent struct {
	Id       string
	Name     string
	DateTime time.Time
	Type     NodeStatusType
}

type NodeEventQuery struct {
	Name     string
	DateTime string
	Type     string
}

type RemoteEvent struct {
	Event      NodeEvent
	SourceNode string
}
