                    # Generate recommendations
                    insights["recommendations"] = self._generate_recommendations(
                        insights["patterns"],
                        insights["metrics"],
                        insights["relationships"]
                    )
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get alert insights: {e}")
            return {
                "relationships": [],
                "patterns": [],
                "metrics": {},
                "recommendations": []
            }

    def _analyze_metrics(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze alert metrics.
        
        Args:
            metrics: Alert metrics
            
        Returns:
            Metric analysis
        """
        analysis = {}
        
        try:
            for metric, value in metrics.items():
                # Get historical values
                historical = self._get_metric_history(metric)
                
                if historical:
                    analysis[metric] = {
                        "current": value,
                        "min": min(historical),
                        "max": max(historical),
                        "avg": sum(historical) / len(historical),
                        "trend": self._calculate_trend(historical + [value]),
                        "anomaly_score": self._calculate_anomaly_score(
                            value,
                            historical
                        )
                    }
                else:
                    analysis[metric] = {
                        "current": value,
                        "trend": "unknown",
                        "anomaly_score": 0
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {e}")
            return {}

    def _get_metric_history(
        self,
        metric: str,
        hours: int = 24
    ) -> List[float]:
        """Get historical metric values.
        
        Args:
            metric: Metric name
            hours: History window in hours
            
        Returns:
            List of historical values
        """
        values = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT metrics
                FROM alerts
                WHERE created_at >= datetime('now', ?)
                ORDER BY created_at ASC
                """, (f"-{hours} hours",))
                
                for row in cursor.fetchall():
                    metrics = json.loads(row[0])
                    if metric in metrics:
                        values.append(metrics[metric])
            
            return values
            
        except Exception as e:
            logger.error(f"Failed to get metric history: {e}")
            return values

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate metric trend.
        
        Args:
            values: Metric values
            
        Returns:
            Trend description
        """
        try:
            if len(values) < 2:
                return "unknown"
            
            # Calculate moving average
            window = min(len(values), 5)
            ma = []
            for i in range(len(values) - window + 1):
                ma.append(sum(values[i:i+window]) / window)
            
            # Calculate trend
            if len(ma) < 2:
                return "stable"
            
            slope = (ma[-1] - ma[0]) / len(ma)
            
            if abs(slope) < 0.01:
                return "stable"
            elif slope > 0:
                return "increasing"
            else:
                return "decreasing"
            
        except Exception as e:
            logger.error(f"Failed to calculate trend: {e}")
            return "unknown"

    def _calculate_anomaly_score(
        self,
        value: float,
        historical: List[float]
    ) -> float:
        """Calculate metric anomaly score.
        
        Args:
            value: Current value
            historical: Historical values
            
        Returns:
            Anomaly score (0-1)
        """
        try:
            if not historical:
                return 0
            
            # Calculate z-score
            mean = sum(historical) / len(historical)
            std = np.std(historical) if len(historical) > 1 else 1
            
            if std == 0:
                return 0
            
            z_score = abs(value - mean) / std
            
            # Convert to score between 0 and 1
            return min(1.0, z_score / 3.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate anomaly score: {e}")
            return 0

    def _generate_recommendations(
        self,
        patterns: List[str],
        metrics: Dict[str, Any],
        relationships: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate alert recommendations.
        
        Args:
            patterns: Matching patterns
            metrics: Metric analysis
            relationships: Alert relationships
            
        Returns:
            List of recommendations
        """
        recommendations = set()
        
        try:
            # Check patterns
            for pattern in patterns:
                for rule in self.rules.values():
                    if pattern in rule.patterns:
                        recommendations.update(
                            self._get_rule_recommendations(rule)
                        )
            
            # Check metrics
            for metric, analysis in metrics.items():
                if analysis.get("anomaly_score", 0) > 0.8:
                    recommendations.add(
                        f"Investigate abnormal {metric} value"
                    )
                
                if analysis.get("trend") == "increasing":
                    recommendations.add(
                        f"Monitor increasing {metric} trend"
                    )
            
            # Check relationships
            causal = [
                r for r in relationships
                if r["type"] == "causes"
            ]
            if causal:
                recommendations.add(
                    "Investigate potential root causes"
                )
            
            return sorted(recommendations)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return list(recommendations)

    def _get_rule_recommendations(self, rule: CorrelationRule) -> List[str]:
        """Get recommendations for correlation rule.
        
        Args:
            rule: Correlation rule
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Add rule-specific recommendations
            if "high_cpu" in rule.metrics:
                recommendations.extend([
                    "Check system resource usage",
                    "Review resource limits",
                    "Monitor process CPU usage"
                ])
            
            if "memory" in rule.metrics:
                recommendations.extend([
                    "Check memory usage",
                    "Review memory limits",
                    "Monitor memory leaks"
                ])
            
            if "error_rate" in rule.metrics:
                recommendations.extend([
                    "Review error logs",
                    "Check application logs",
                    "Monitor error trends"
                ])
            
            # Add custom recommendations
            if "recommendations" in rule.conditions:
                recommendations.extend(rule.conditions["recommendations"])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get rule recommendations: {e}")
            return []

    def export_graph(self, format: str = "graphviz") -> str:
        """Export alert relationship graph.
        
        Args:
            format: Export format
            
        Returns:
            Graph representation
        """
        try:
            if format == "graphviz":
                return nx.nx_pydot.to_pydot(self.alert_graph).to_string()
            elif format == "json":
                return json.dumps({
                    "nodes": list(self.alert_graph.nodes()),
                    "edges": [
                        {
                            "source": u,
                            "target": v,
                            "weight": d["weight"]
                        }
                        for u, v, d in self.alert_graph.edges(data=True)
                    ]
                })
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return ""

    def get_correlation_metrics(self) -> Dict[str, Any]:
        """Get correlation analysis metrics.
        
        Returns:
            Correlation metrics
        """
        try:
            metrics = {
                "alerts": len(self.alert_graph),
                "relationships": self.alert_graph.number_of_edges(),
                "groups": len(self.alert_groups),
                "patterns": len(set().union(*(
                    group.patterns for group in self.alert_groups.values()
                ))),
                "clustering": nx.average_clustering(self.alert_graph),
                "components": nx.number_connected_components(
                    self.alert_graph.to_undirected()
                )
            }
            
            # Calculate centrality
            if len(self.alert_graph) > 0:
                centrality = nx.degree_centrality(self.alert_graph)
                metrics["max_centrality"] = max(centrality.values())
                metrics["avg_centrality"] = sum(centrality.values()) / len(centrality)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get correlation metrics: {e}")
            return {}
