import 'package:flutter_test/flutter_test.dart';
import 'package:getgoals_frontend/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const UngDungGetGoals());
    expect(find.byType(UngDungGetGoals), findsOneWidget);
  });
}
