package middleware

import (
	"net/http"
	"sync"
	"time"
)

// RateLimiter provides per-client request rate limiting
type RateLimiter struct {
	mu       sync.Mutex
	clients  map[string]*clientInfo
	limit    int
	window   time.Duration
}

type clientInfo struct {
	count    int
	lastSeen time.Time
}

// NewRateLimiter creates a new RateLimiter with the given requests-per-window
func NewRateLimiter(limit int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		clients: make(map[string]*clientInfo),
		limit:   limit,
		window:  window,
	}
}

// Middleware returns an HTTP middleware that enforces rate limiting
func (rl *RateLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		clientID := r.RemoteAddr

		rl.mu.Lock()
		defer rl.mu.Unlock()

		info, exists := rl.clients[clientID]
		if !exists || time.Since(info.lastSeen) > rl.window {
			rl.clients[clientID] = &clientInfo{count: 1, lastSeen: time.Now()}
			next.ServeHTTP(w, r)
			return
		}

		if info.count >= rl.limit {
			http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
			return
		}

		info.count++
		info.lastSeen = time.Now()
		next.ServeHTTP(w, r)
	})
}

// CleanupStaleClients removes clients not seen within the given duration
func (rl *RateLimiter) CleanupStaleClients(maxAge time.Duration) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	for id, info := range rl.clients {
		if now.Sub(info.lastSeen) > maxAge {
			delete(rl.clients, id)
		}
	}
}
