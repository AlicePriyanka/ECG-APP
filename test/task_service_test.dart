import 'package:flutter_test/flutter_test.dart';
import 'package:ecg_flutter_app/services/task_service.dart';

void main() {
  test('TaskService.markTaskRead handles network exceptions gracefully', () async {
    // Calling markTaskRead should not throw any exception even if the backend is unreachable or offline
    expect(
      TaskService.markTaskRead(taskId: 99999, doctorId: 99999),
      completes,
    );
  });
}
