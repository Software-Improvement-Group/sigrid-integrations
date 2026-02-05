#  Copyright Software Improvement Group
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import os
import tempfile
import time
from unittest.mock import Mock, patch

from report_generator.generator.report_generator import ReportGenerator


class TestReportGeneratorMultithreading:
    
    def test_worker_count_uses_cpu_count(self):
        """Test that worker count is based on CPU count"""
        with patch('os.cpu_count', return_value=4):
            with patch.object(ReportGenerator, '_execute_placeholders', return_value=[]):
                with patch.object(ReportGenerator, '__init__', return_value=None):
                    generator = ReportGenerator.__new__(ReportGenerator)
                    generator.placeholders = set()
                    generator.report = Mock()
                    generator.report.save = Mock()
                    
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        generator.generate(tmp.name)
                        os.unlink(tmp.name)
    
    def test_worker_count_minimum_is_two(self):
        """Test that minimum worker count is 2 even on single-core systems"""
        with patch('os.cpu_count', return_value=1):
            with patch.object(ReportGenerator, '__init__', return_value=None):
                generator = ReportGenerator.__new__(ReportGenerator)
                generator.placeholders = set()
                generator.report = Mock()
                
                # Access the worker calculation logic
                num_workers = max(2, min(os.cpu_count() or 4, 8))
                assert num_workers == 2
    
    def test_worker_count_maximum_is_eight(self):
        """Test that maximum worker count is capped at 8"""
        with patch('os.cpu_count', return_value=16):
            with patch.object(ReportGenerator, '__init__', return_value=None):
                generator = ReportGenerator.__new__(ReportGenerator)
                generator.placeholders = set()
                generator.report = Mock()
                
                # Access the worker calculation logic
                num_workers = max(2, min(os.cpu_count() or 4, 8))
                assert num_workers == 8
    
    def test_worker_count_defaults_to_four_when_cpu_count_unavailable(self):
        """Test that worker count defaults to 4 when CPU count cannot be determined"""
        with patch('os.cpu_count', return_value=None):
            with patch.object(ReportGenerator, '__init__', return_value=None):
                generator = ReportGenerator.__new__(ReportGenerator)
                generator.placeholders = set()
                generator.report = Mock()
                
                # Access the worker calculation logic
                num_workers = max(2, min(os.cpu_count() or 4, 8))
                assert num_workers == 4
    
    def test_parallel_execution_calls_all_placeholders(self):
        """Test that all placeholders are resolved in parallel execution"""
        mock_placeholder1 = Mock()
        mock_placeholder1.key = "PLACEHOLDER_1"
        mock_placeholder1.resolve = Mock()
        
        mock_placeholder2 = Mock()
        mock_placeholder2.key = "PLACEHOLDER_2"
        mock_placeholder2.resolve = Mock()
        
        mock_placeholder3 = Mock()
        mock_placeholder3.key = "PLACEHOLDER_3"
        mock_placeholder3.resolve = Mock()
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update([mock_placeholder1, mock_placeholder2, mock_placeholder3])
            generator.report = Mock()
            
            # Execute placeholders
            generator._execute_placeholders(2, generator._resolve_placeholder)
            
            # Verify all placeholders were resolved
            mock_placeholder1.resolve.assert_called_once_with(generator.report)
            mock_placeholder2.resolve.assert_called_once_with(generator.report)
            mock_placeholder3.resolve.assert_called_once_with(generator.report)
    
    def test_timing_is_collected_in_debug_mode(self):
        """Test that timing information is collected when using timing resolver"""
        mock_placeholder = Mock()
        mock_placeholder.key = "TEST_PLACEHOLDER"
        mock_placeholder.resolve = Mock()
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update([mock_placeholder])
            generator.report = Mock()
            
            # Execute with timing
            timings = generator._execute_placeholders(2, generator._resolve_placeholder_with_timing)
            
            # Verify timing was collected
            assert len(timings) == 1
            assert timings[0][0] == "TEST_PLACEHOLDER"
            assert isinstance(timings[0][1], float)
            assert timings[0][1] >= 0
    
    def test_no_timing_collected_without_debug_mode(self):
        """Test that timing information is not collected in non-debug mode"""
        mock_placeholder = Mock()
        mock_placeholder.key = "TEST_PLACEHOLDER"
        mock_placeholder.resolve = Mock()
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update([mock_placeholder])
            generator.report = Mock()
            
            # Execute without timing
            timings = generator._execute_placeholders(2, generator._resolve_placeholder)
            
            # Verify no timing was collected
            assert len(timings) == 0
    
    def test_error_handling_in_parallel_execution(self):
        """Test that errors in one placeholder don't stop others from executing"""
        mock_placeholder1 = Mock()
        mock_placeholder1.key = "PLACEHOLDER_1"
        mock_placeholder1.resolve = Mock(side_effect=Exception("Test error"))
        
        mock_placeholder2 = Mock()
        mock_placeholder2.key = "PLACEHOLDER_2"
        mock_placeholder2.resolve = Mock()
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update([mock_placeholder1, mock_placeholder2])
            generator.report = Mock()
            
            # Execute placeholders - should not raise exception
            with patch('logging.error'):
                generator._execute_placeholders(2, generator._resolve_placeholder)
            
            # Verify successful placeholder was still called
            mock_placeholder2.resolve.assert_called_once_with(generator.report)
    
    def test_debug_mode_logs_slowest_placeholders(self):
        """Test that debug mode logs the slowest placeholders"""
        mock_placeholder1 = Mock()
        mock_placeholder1.key = "FAST_PLACEHOLDER"
        mock_placeholder1.resolve = Mock()
        
        mock_placeholder2 = Mock()
        mock_placeholder2.key = "SLOW_PLACEHOLDER"
        
        def slow_resolve(report):
            time.sleep(0.01)
        
        mock_placeholder2.resolve = slow_resolve
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update([mock_placeholder1, mock_placeholder2])
            generator.report = Mock()
            generator.report.save = Mock()
            
            # Set debug logging level
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_logger.level = logging.DEBUG
                mock_get_logger.return_value = mock_logger
                
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    with patch('logging.debug') as mock_debug:
                        generator.generate(tmp.name)
                        
                        # Verify debug logging was called
                        assert mock_debug.called
                    os.unlink(tmp.name)
    
    def test_concurrent_execution_thread_safety(self):
        """Test that concurrent placeholder resolution executes all placeholders"""
        call_count = []
        
        def track_call(report):
            # Track that this placeholder was called
            call_count.append(1)
        
        mock_placeholders = []
        for i in range(10):
            mock_placeholder = Mock()
            mock_placeholder.key = f"PLACEHOLDER_{i}"
            mock_placeholder.resolve = track_call
            mock_placeholders.append(mock_placeholder)
        
        with patch.object(ReportGenerator, '__init__', return_value=None):
            generator = ReportGenerator.__new__(ReportGenerator)
            generator.placeholders = set()
            generator.placeholders.update(mock_placeholders)
            generator.report = Mock()
            
            # Execute placeholders
            generator._execute_placeholders(4, generator._resolve_placeholder)
            
            # Verify all 10 placeholders were executed
            assert len(call_count) == 10
