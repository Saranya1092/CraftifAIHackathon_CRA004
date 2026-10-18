"""Tests for perception adapters."""
import pytest

from app.perception.simulated_adapter import SimulatedAdapter
from app.perception.adapter_factory import get_adapter
from app.perception.pipegen_adapter import PipeGenAdapter, PERSON_CLASS_IDS


class TestSimulatedAdapter:
    @pytest.mark.asyncio
    async def test_simulated_yields_detections(self):
        adapter = SimulatedAdapter(fps=100.0)
        gen = adapter.stream()
        detections = await gen.__anext__()
        assert isinstance(detections, list)
        assert len(detections) >= 1
        det = detections[0]
        assert "class" in det
        assert "confidence" in det
        assert "cx" in det
        assert "cy" in det
        assert "bbox" in det
        assert det["source"] == "simulated"

    @pytest.mark.asyncio
    async def test_simulated_confidence_range(self):
        adapter = SimulatedAdapter(fps=100.0)
        gen = adapter.stream()
        for _ in range(10):
            detections = await gen.__anext__()
            for d in detections:
                assert 0.0 <= d["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_simulated_bbox_normalised(self):
        adapter = SimulatedAdapter(fps=100.0)
        gen = adapter.stream()
        detections = await gen.__anext__()
        d = detections[0]
        x1, y1, x2, y2 = d["bbox"]
        assert 0.0 <= x1 <= x2 <= 1.0
        assert 0.0 <= y1 <= y2 <= 1.0


class TestAdapterFactory:
    def test_simulated_returns_simulated_adapter(self):
        adapter = get_adapter("simulated")
        assert isinstance(adapter, SimulatedAdapter)

    def test_pipegen_returns_pipegen_adapter(self):
        adapter = get_adapter("pipegen")
        assert isinstance(adapter, PipeGenAdapter)

    def test_deepstream_alias_returns_pipegen_adapter(self):
        adapter = get_adapter("deepstream")
        assert isinstance(adapter, PipeGenAdapter)

    def test_unknown_adapter_raises(self):
        with pytest.raises(ValueError, match="Unknown perception adapter"):
            get_adapter("unicorn")


class TestPipeGenAdapterParser:
    def test_parse_valid_frame(self):
        adapter = PipeGenAdapter()
        raw = {
            "frame_num": 42,
            "stream_id": 0,
            "objects": [
                {
                    "class_id": 0,
                    "class_label": "person",
                    "confidence": 0.88,
                    "bbox": {"left": 192, "top": 108, "width": 192, "height": 324},
                }
            ],
        }
        detections = adapter._parse_frame(raw)
        assert len(detections) == 1
        d = detections[0]
        assert d["class"] == "person"
        assert d["confidence"] == 0.88
        assert 0.0 <= d["cx"] <= 1.0
        assert 0.0 <= d["cy"] <= 1.0

    def test_low_confidence_filtered(self):
        adapter = PipeGenAdapter()
        raw = {
            "frame_num": 1,
            "objects": [
                {
                    "class_id": 0,
                    "class_label": "person",
                    "confidence": 0.1,  # below threshold
                    "bbox": {"left": 0, "top": 0, "width": 100, "height": 100},
                }
            ],
        }
        assert adapter._parse_frame(raw) == []

    def test_non_person_class_filtered(self):
        adapter = PipeGenAdapter()
        raw = {
            "frame_num": 1,
            "objects": [
                {
                    "class_id": 1,
                    "class_label": "car",
                    "confidence": 0.95,
                    "bbox": {"left": 0, "top": 0, "width": 100, "height": 100},
                }
            ],
        }
        assert adapter._parse_frame(raw) == []

    def test_empty_objects(self):
        adapter = PipeGenAdapter()
        assert adapter._parse_frame({"frame_num": 1, "objects": []}) == []

    def test_malformed_frame_returns_empty(self):
        adapter = PipeGenAdapter()
        assert adapter._parse_frame({}) == []
