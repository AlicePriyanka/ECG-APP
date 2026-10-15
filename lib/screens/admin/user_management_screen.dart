import 'package:flutter/material.dart';
import '../../services/admin_service.dart';

class UserManagementScreen extends StatefulWidget {
  const UserManagementScreen({super.key});

  @override
  State<UserManagementScreen> createState() => _UserManagementScreenState();
}

class _UserManagementScreenState extends State<UserManagementScreen>
    with SingleTickerProviderStateMixin {
  static const _primaryColor = Color(0xFF3A418E); // Match main theme
  late TabController _tabController;
  List<Map<String, dynamic>> _users = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    // 4 Tabs: Pending, Active, Blocked, Rejected
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(_filterUsers);
    _fetchUsers();
  }

  Future<void> _fetchUsers() async {
    setState(() => _isLoading = true);
    final users = await AdminService.fetchUsers();
    if (mounted) {
      setState(() {
        _users = users;
        _isLoading = false;
      });
    }
  }

  void _filterUsers() {
    setState(() {});
  }

  List<Map<String, dynamic>> _getFilteredUsers() {
    String statusFilter;
    switch (_tabController.index) {
      case 0:
        statusFilter = 'pending';
        break;
      case 1:
        statusFilter = 'active';
        break;
      case 2:
        statusFilter = 'blocked';
        break;
      case 3:
        statusFilter = 'rejected';
        break;
      default:
        statusFilter = 'all';
    }

    return _users.where((u) {
      final active = int.tryParse(u['active'].toString()) ?? 0;
      final blocked = int.tryParse(u['blocked'].toString()) ?? 0;

      // STRICT Filtering matching user request
      if (statusFilter == 'pending') return active == 0 && blocked == 0;
      if (statusFilter == 'active') return active == 1 && blocked == 0;
      if (statusFilter == 'blocked') return active == 1 && blocked == 1;
      if (statusFilter == 'rejected') return active == 0 && blocked == 1;

      return true;
    }).toList();
  }

  Future<void> _updateStatus(String userId, String action) async {
    final success = await AdminService.updateUserStatus(userId, action);
    if (success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('User status updated: $action')));
      }
      _fetchUsers();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Failed to update')));
      }
    }
  }

  String _getInitials(String name) {
    if (name.isEmpty) return 'U';
    final names = name.split(' ');
    if (names.length >= 2) {
      return '${names[0][0]}${names[1][0]}'.toUpperCase();
    }
    return names[0][0].toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    final filteredUsers = _getFilteredUsers();
    final currentTabName = _getTabName(_tabController.index).toUpperCase();

    return Scaffold(
      appBar: AppBar(
        title: const Text('User Management'),
        backgroundColor: _primaryColor,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchUsers,
            tooltip: 'Refresh',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Pending'),
            Tab(text: 'Active'),
            Tab(text: 'Blocked'),
            Tab(text: 'Rejected'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : filteredUsers.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.people_outline,
                          size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        'No $currentTabName users found',
                        style:
                            const TextStyle(color: Colors.grey, fontSize: 16),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: filteredUsers.length,
                  itemBuilder: (context, index) {
                    final user = filteredUsers[index];
                    final name = user['name'] ?? 'Unknown';
                    return Card(
                      elevation: 2,
                      margin: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _primaryColor.withOpacity(0.1),
                          child: Text(
                            _getInitials(name),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: _primaryColor,
                            ),
                          ),
                        ),
                        title: Text(
                          name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Colors.black87,
                          ),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                const Icon(Icons.email,
                                    size: 14, color: Colors.grey),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    user['email'] ?? '',
                                    style: TextStyle(color: Colors.grey[700]),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                const Icon(Icons.badge,
                                    size: 14, color: Colors.grey),
                                const SizedBox(width: 4),
                                Text(
                                  'Role: ${(user['role'] as String).toUpperCase()}',
                                  style: TextStyle(
                                      color: Colors.grey[700],
                                      fontWeight: FontWeight.w500),
                                ),
                              ],
                            ),
                            if (user['phone'] != null &&
                                user['phone'].toString().isNotEmpty) ...[
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.phone,
                                      size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text(
                                    user['phone'],
                                    style: TextStyle(color: Colors.grey[700]),
                                  ),
                                ],
                              ),
                            ],
                          ],
                        ),
                        trailing: _buildActions(user),
                        isThreeLine: true,
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 8),
                      ),
                    );
                  },
                ),
    );
  }

  String _getTabName(int index) {
    switch (index) {
      case 0:
        return 'pending';
      case 1:
        return 'active';
      case 2:
        return 'blocked';
      case 3:
        return 'rejected';
      default:
        return 'unknown';
    }
  }

  Widget _buildActions(Map<String, dynamic> user) {
    final userId = user['id'].toString();
    final active = int.tryParse(user['active'].toString()) ?? 0;
    final blocked = int.tryParse(user['blocked'].toString()) ?? 0;

    // --- Blocked Tab Actions (1,1) ---
    if (active == 1 && blocked == 1) {
      return IconButton(
        icon: const Icon(Icons.restore, color: Colors.green),
        onPressed: () =>
            _updateStatus(userId, 'unblock'), // Become Active (1,0)
        tooltip: 'Unblock (Activate)',
      );
    }

    // --- Rejected Tab Actions (0,1) ---
    if (active == 0 && blocked == 1) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.check, color: Colors.green),
            onPressed: () =>
                _updateStatus(userId, 'approve'), // Become Active (1,0)
            tooltip: 'Approve',
          ),
          IconButton(
            icon: const Icon(Icons.delete, color: Colors.grey),
            onPressed: () =>
                _updateStatus(userId, 'delete'), // Permanently Delete
            tooltip: 'Delete',
          ),
        ],
      );
    }

    // --- Pending Tab Actions (0,0) ---
    if (active == 0 && blocked == 0) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.check, color: Colors.green),
            onPressed: () =>
                _updateStatus(userId, 'approve'), // Become Active (1,0)
            tooltip: 'Approve',
          ),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.red),
            onPressed: () =>
                _updateStatus(userId, 'reject'), // Become Rejected (0,1)
            tooltip: 'Reject',
          ),
        ],
      );
    }

    // --- Active Tab Actions (1,0) ---
    if (active == 1 && blocked == 0) {
      return IconButton(
        icon: const Icon(Icons.block, color: Colors.red),
        onPressed: () => _updateStatus(userId, 'block'), // Become Blocked (1,1)
        tooltip: 'Block',
      );
    }

    return const SizedBox.shrink();
  }
}
