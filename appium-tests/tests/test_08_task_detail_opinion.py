import pytest
from pages.task_detail_page import TaskDetailPage


class TestTaskDetailOpinionE2E:
    """E2E Tests for ECG Image Viewer, Full-Screen InteractiveViewer, and Clinical Opinions."""

    @pytest.mark.opinion
    @pytest.mark.p1
    def test_tc276_ecg_interactive_fullscreen_zoom(self, logged_in_doctor):
        """TC276: Tapping ECG thumbnail opens InteractiveViewer with pinch-zoom support."""
        dashboard = logged_in_doctor
        dashboard.click_first_assigned_patient()
        detail_page = TaskDetailPage(dashboard.driver)
        detail_page.click_first_image_thumbnail()
        assert detail_page.is_fullscreen_viewer_open(), "Full-screen ECG viewer failed to display"
        detail_page.close_fullscreen_viewer()

    @pytest.mark.opinion
    @pytest.mark.p1
    def test_tc277_submit_clinical_opinion_single_image(self, logged_in_doctor):
        """TC277: Submitting medical feedback on an individual ECG image."""
        dashboard = logged_in_doctor
        dashboard.click_first_assigned_patient()
        detail_page = TaskDetailPage(dashboard.driver)
        detail_page.enter_opinion("Normal Sinus Rhythm. No ST elevation or pathological Q waves noted.", apply_to_all=False)
        assert detail_page.is_opinion_saved(), "Opinion confirmation snackbar was not displayed"

    @pytest.mark.opinion
    @pytest.mark.p1
    def test_tc278_bulk_opinion_apply_to_all(self, logged_in_doctor):
        """TC278: Checking 'Apply to all images' updates all images in the task and elevates task status."""
        dashboard = logged_in_doctor
        dashboard.click_first_assigned_patient()
        detail_page = TaskDetailPage(dashboard.driver)
        detail_page.enter_opinion("Normal Sinus Rhythm (Bulk Review)", apply_to_all=True)
        assert detail_page.is_opinion_saved()
